import os

import urlparse
import redis

class RedisConnection(object):

  CONNECTION = None

  @staticmethod
  def getConnection():
    if not RedisConnection.CONNECTION:
      if 'REDIS_URL' in os.environ:
        url = urlparse.urlparse(url=os.environ['REDIS_URL'])
        RedisConnection.CONNECTION = redis.Redis(host=url.hostname, port=url.port)
      else:
        redis_url = redis.Redis('localhost', port=6379)

    return RedisConnection.CONNECTION

  @staticmethod
  def hset(name, key, value):
    return RedisConnection.getConnection().hset(name, key, value)

  @staticmethod
  def hget(name, key):
    return RedisConnection.getConnection().hget(name, key)

  @staticmethod
  def set(key, value):
    return RedisConnection.getConnection().set(key, value)

  @staticmethod
  def get(key):
    return RedisConnection.getConnection().get(key)

  @staticmethod
  def delete(names):
    return RedisConnection.getConnection().delete(names)
