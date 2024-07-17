from typing import Dict, List
import redis
import logging

from master.database.Repository import Repository
from master.conf.config import REDIS_HOST, REDIS_PORT
from master.conf.logging_config import setup_logging

class Redis(Repository):
    """Concrete implementation of Repository using Redis."""

    def __init__(self) -> None:
        log_file = f'logs/master_app.log'
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize Redis connection using configured host and port.
        try:
            self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
            # Check the connection
            if not self.redis_conn.ping():
                raise ConnectionError("Unable to connect to Redis")
            self.logger.info("Connected to Redis successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Redis connection: {e}")
            raise

    def create(self, key: str, data: Dict[str, str]) -> None:
        """Save data to Redis under the given key."""
        # Convert all values to strings
        try:
            data = {k: str(v) for k, v in data.items()}
            self.redis_conn.hset(key, mapping=data)
            self.logger.info(f"Data created in Redis for key: {key}")

        except Exception as e:
            self.logger.error(f"Error in create method: {e}")
            raise

    def read(self, key: str) -> Dict[str, str]:
        """Load data from Redis using the given key."""
        try:
            data = self.redis_conn.hgetall(key)
            result = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
            self.logger.info(f"Data read from Redis for key: {key}")
            return result

        except Exception as e:
            self.logger.error(f"Error in read method: {e}")
            raise

    def read_all(self) -> List[str]:
        """Get all keys stored in the Redis database."""
        try:
            keys = self.redis_conn.keys()
            result = [key.decode('utf-8') for key in keys]
            self.logger.info("All keys read from Redis")
            return result

        except Exception as e:
            self.logger.error(f"Error in read_all method: {e}")
            raise

    def update(self, key: str, data: Dict[str, str]) -> None:
        """Update data in Redis under the given key"""
        try:
            # Convert all values to strings
            data = {k: str(v) for k, v in data.items()}
            self.redis_conn.hset(key, mapping=data)
            self.logger.info(f"Data updated in Redis for key: {key}")

        except Exception as e:
            self.logger.error(f"Error in update method: {e}")
            raise

    def delete(self, key: str) -> None:
        """Delete data from Redis using the given key."""
        try:
            self.redis_conn.delete(key)
            self.logger.info(f"Data deleted from Redis for key: {key}")

        except Exception as e:
            self.logger.error(f"Error in delete method: {e}")
            raise
