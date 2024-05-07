import redis
from typing import Dict, List

class DB:
    def __init__(self) -> None:
        self.redis_conn = redis.Redis(host='localhost', port=6379)

    def save_data(self, key: str, data: Dict[str,str]) -> None:
        """Save data to Redis under the given key."""
        self.redis_conn.hmset(key, data)

    def load_data(self, key:str) -> Dict[str, str]:
        """Load data from Redis using the given key."""
        data = self.redis_conn.hgetall(key)
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
    
    def get_all_ids(self) -> List[str]:
        """Get all keys stored in the Redis database."""
        keys = self.redis_conn.keys()
        return [key.decode('utf-8') for key in keys]
