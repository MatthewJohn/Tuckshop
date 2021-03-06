import os

import urlparse
import redis


class LocalRedis(object):

    def __init__(self):
        self.cache = {}

    def hset(self, name, key, value):
        if (name not in self.cache):
            self.cache[name] = {}
        self.cache[name][key] = value
        return True

    def hget(self, name, key):
        if (name in self.cache and key in self.cache[name]):
            return self.cache[name][key]
        else:
            return None

    def hdel(self, name, keys):
        if name in self.cache:
            for key in keys:
                if key in self.cache[name]:
                    del(self.cache[name][key])

    def set(self, key, value):
        self.cache[key] = value
        return True

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def delete(self, names):
        for name in names:
            if name in self.cache:
                del(self.cache[name])

        return True

    def exists(self, name):
        return (name in self.cache)

    def flushdb(self):
        self.cache = {}


class RedisConnection(object):

    CONNECTION = None

    @staticmethod
    def _getConnection():
        if not RedisConnection.CONNECTION:
            if 'REDIS_URL' in os.environ:
                RedisConnection.CONNECTION = redis.Redis.from_url(url=os.environ['REDIS_URL'])
            else:
                RedisConnection.CONNECTION = LocalRedis()

        return RedisConnection.CONNECTION

    @staticmethod
    def hset(name, key, value):
        return RedisConnection._getConnection().hset(name, key, value)

    @staticmethod
    def hget(name, key):
        return RedisConnection._getConnection().hget(name, key)

    @staticmethod
    def hdel(name, keys):
        return RedisConnection._getConnection().hdel(name, keys)

    @staticmethod
    def set(key, value):
        return RedisConnection._getConnection().set(key, value)

    @staticmethod
    def get(key):
        return RedisConnection._getConnection().get(key)

    @staticmethod
    def delete(names):
        return RedisConnection._getConnection().delete(names)

    @staticmethod
    def exists(name):
        return RedisConnection._getConnection().exists(name)

    @staticmethod
    def flushdb():
        return RedisConnection._getConnection().flushdb()
