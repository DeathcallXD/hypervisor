import redis


class RedisManager:
    def __init__(self, host, port, password=None, ssl=False):
        self.host = host
        self.port = port
        self.password = password
        self.ssl = ssl
        self.redis_client = self._create_connection()

    def _create_connection(self):
        return redis.StrictRedis(
            host=self.host,
            port=self.port,
            password=self.password,
            ssl=self.ssl,
            decode_responses=True,
        )

    def set_key(self, key, value):
        self.redis_client.set(key, value)

    def set_key_with_expiry(self, key, value, ttl):
        self.redis_client.set(key, value, ex=ttl)

    def get_key(self, key):
        return self.redis_client.get(key)
    
    def hget_key(self,name, key):
        return self.redis_client.hget(name, key)

    def update_key(self, key, value):
        self.redis_client.set(key, value)

    def close_connection(self):
        self.redis_client.close()

    def delete_key(self, key):
        self.redis_client.delete(key)
    
    def increment_key(self, key, incr_by=1):
        self.redis_client.incrby(key, incr_by)
