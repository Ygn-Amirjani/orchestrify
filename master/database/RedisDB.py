from master.database.Repository import Repository
from typing import Dict, List
from master.conf.config import REDIS_HOST, REDIS_PORT
import redis

class Redis(Repository):
    """Concrete implementation of Repository using Redis."""

    def __init__(self) -> None:
        """Initialize Redis connection using configured host and port."""
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    def create(self, key: str, data: Dict[str, str]) -> None:
        """Save data to Redis under the given key."""
        self.redis_conn.hmset(key, data)

    def read(self, key: str) -> Dict[str, str]:
        """Load data from Redis using the given key."""
        data = self.redis_conn.hgetall(key)
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
    
    def read_all(self) -> List[str]:
        """Get all keys stored in the Redis database."""
        keys = self.redis_conn.keys()
        return [key.decode('utf-8') for key in keys]

    def update(self, key: str, data: Dict[str, str]) -> None:
        """Update data in Redis under the given key"""
        self.redis_conn.hmset(key, data)

    def delete(self, key: str) -> None:
        """Delete data from Redis using the given key."""
        self.redis_conn.delete(key)
