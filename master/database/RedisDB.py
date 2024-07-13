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
        # Convert all values to strings
        try:
            data = {k: str(v) for k, v in data.items()}
            self.redis_conn.hset(key, mapping=data)

        except Exception as e:
            print(f"Error in create method: {e}")
            raise

    def read(self, key: str) -> Dict[str, str]:
        """Load data from Redis using the given key."""
        try:
            data = self.redis_conn.hgetall(key)
            return {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}

        except Exception as e:
            print(f"Error in read method: {e}")
            raise

    def read_all(self) -> List[str]:
        """Get all keys stored in the Redis database."""
        try:
            keys = self.redis_conn.keys()
            return [key.decode('utf-8') for key in keys]

        except Exception as e:
            print(f"Error in read_all method: {e}")
            raise

    def update(self, key: str, data: Dict[str, str]) -> None:
        """Update data in Redis under the given key"""
        try:
            # Convert all values to strings
            data = {k: str(v) for k, v in data.items()}
            self.redis_conn.hset(key, mapping=data)

        except Exception as e:
            print(f"Error in update method: {e}")
            raise

    def delete(self, key: str) -> None:
        """Delete data from Redis using the given key."""
        try:
            self.redis_conn.delete(key)

        except Exception as e:
            print(f"Error in delete method: {e}")
            raise
