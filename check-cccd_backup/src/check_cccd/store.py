from typing import Optional, Dict, List
from datetime import datetime, timedelta


class InMemoryStore:
    """Simple in-memory store for demo and tests."""
    
    def __init__(self):
        self._status = {}
        self._results = {}
    
    def save_status(self, request_id: str, status: str):
        self._status[request_id] = status
    
    def get_status(self, request_id: str) -> Optional[str]:
        return self._status.get(request_id)
    
    def save_result(self, request_id: str, result: Dict):
        self._results[request_id] = result
    
    def get_result(self, request_id: str) -> Optional[Dict]:
        return self._results.get(request_id)
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict]:
        return []
    
    def cleanup_old_data(self, days: int = 30):
        pass