import hashlib
import time
from typing import Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db, get_redis
from .models import ApiKey
from .config import settings

security = HTTPBearer(auto_error=False)


def hash_api_key(key: str) -> str:
    """Hash API key for storage."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(key_hash: str, provided_key: str) -> bool:
    """Verify API key against stored hash."""
    return hash_api_key(provided_key) == key_hash


async def get_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[str]:
    """Extract and validate API key from request."""
    if not credentials:
        return None
    
    if not credentials.scheme.lower() == "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    # Hash the provided key
    key_hash = hash_api_key(credentials.credentials)
    
    # Check if key exists and is active
    api_key = db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Update last used timestamp
    api_key.last_used_at = time.time()
    db.commit()
    
    return credentials.credentials


def check_rate_limit(api_key: str, redis_client) -> bool:
    """Check if request is within rate limit."""
    if not api_key:
        return False
    
    key_hash = hash_api_key(api_key)
    current_time = int(time.time())
    minute_window = current_time // 60
    
    # Rate limit key
    rate_key = f"rate_limit:{key_hash}:{minute_window}"
    
    # Get current count
    current_count = redis_client.get(rate_key)
    if current_count is None:
        current_count = 0
    else:
        current_count = int(current_count)
    
    # Check if limit exceeded
    if current_count >= settings.rate_limit_per_minute:
        return False
    
    # Increment counter
    redis_client.incr(rate_key)
    redis_client.expire(rate_key, 60)  # Expire after 1 minute
    
    return True


async def require_api_key(
    api_key: Optional[str] = Depends(get_api_key),
    request: Request = None
) -> str:
    """Require valid API key for protected endpoints."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Check rate limit
    redis_client = get_redis()
    if not check_rate_limit(api_key, redis_client):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return api_key