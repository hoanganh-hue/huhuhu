from celery import Celery
from sqlalchemy.orm import sessionmaker
from .config import settings
from .database import engine, get_redis
from .scraper import scrape_cccd_sync
from .store import DatabaseStore
from .logging import logger, metrics
import time

# Create Celery app
celery_app = Celery(
    'check_cccd_worker',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['check_cccd.worker']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_routes={
        'check_cccd.worker.process_cccd_task': {'queue': 'cccd_processing'},
    }
)

# Create database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True, name='check_cccd.worker.process_cccd_task')
def process_cccd_task(self, request_id: str, cccd: str):
    """Process CCCD check in background."""
    start_time = time.time()
    
    try:
        # Create database session
        db = SessionLocal()
        store = DatabaseStore(db)
        
        # Update status to processing
        store.save_status(request_id, 'processing')
        
        # Perform scraping
        logger.info("Starting CCCD processing", request_id=request_id, cccd=cccd)
        
        result = scrape_cccd_sync(cccd)
        result['request_id'] = request_id
        
        # Save result
        store.save_result(request_id, result)
        store.save_status(request_id, 'completed')
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info("CCCD processing completed", 
                   request_id=request_id, 
                   cccd=cccd,
                   status=result.get('status'),
                   duration_ms=duration_ms,
                   matches_count=len(result.get('matches', [])))
        
        # Update metrics
        metrics.increment_counter("worker_tasks_completed", tags={"status": "success"})
        metrics.record_histogram("worker_task_duration_ms", duration_ms)
        
        db.close()
        return result
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        # Update status to error
        try:
            db = SessionLocal()
            store = DatabaseStore(db)
            store.save_status(request_id, 'error')
            store.save_result(request_id, {
                "request_id": request_id,
                "id_cccd": cccd,
                "status": "error",
                "error_message": str(e),
                "matches": []
            })
            db.close()
        except Exception as db_error:
            logger.error("Failed to save error status", 
                        request_id=request_id, 
                        error=str(db_error))
        
        logger.error("CCCD processing failed", 
                    request_id=request_id, 
                    cccd=cccd,
                    error=str(e),
                    duration_ms=duration_ms)
        
        # Update metrics
        metrics.increment_counter("worker_tasks_completed", tags={"status": "error"})
        metrics.increment_counter("worker_task_errors")
        
        # Re-raise for Celery retry mechanism
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(name='check_cccd.worker.cleanup_old_data')
def cleanup_old_data_task(days: int = 30):
    """Clean up old data."""
    try:
        db = SessionLocal()
        store = DatabaseStore(db)
        store.cleanup_old_data(days)
        db.close()
        
        logger.info("Cleanup task completed", days=days)
        
    except Exception as e:
        logger.error("Cleanup task failed", error=str(e))
        raise


@celery_app.task(name='check_cccd.worker.health_check')
def health_check_task():
    """Health check task."""
    try:
        # Check Redis connection
        redis_client = get_redis()
        redis_client.ping()
        
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        logger.info("Health check passed")
        return {"status": "healthy", "timestamp": time.time()}
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}


# Periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-old-data': {
        'task': 'check_cccd.worker.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'args': (30,)  # Keep data for 30 days
    },
    'health-check': {
        'task': 'check_cccd.worker.health_check',
        'schedule': 60.0,  # Every minute
    },
}