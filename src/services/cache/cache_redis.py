import redis

from src.services.cache.cache_interface import Cache


class RedisCache(Cache):
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 6379,
                 rate_limit: int = 3,
                 time_in_seconds: int = 60 * 60 * 24):
        self._redis = redis.Redis(
            host=host, port=port)

        self.rate_limit = rate_limit
        self.time_in_seconds = time_in_seconds

    def get(self, key: str) -> str:
        return self._redis.get(key)

    def set(self, key: str, value: str) -> None:
        self._redis.set(key, value)

    def delete(self, key: str) -> None:
        self._redis.delete(key)

    def exists(self, key: str) -> bool:
        return self._redis.exists(key)

    def request_is_limited(self, key: str) -> bool:

        if self.exists(key):
            bucket_value = self.get(key)
            if int(bucket_value) >= self.rate_limit:
                return True
            else:
                self.set(key, int(bucket_value) + 1)
                return False
        else:
            self.set(key, 1)
            self._redis.expire(key, self.time_in_seconds)
            return False
