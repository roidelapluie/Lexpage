from django.conf import settings
from websockets_helpers import FakeRedisPublisher
from ws4redis.publisher import RedisPublisher as RealRedisPublisher
import logging

if hasattr(settings, 'WS4REDIS_SUBSCRIBER') and settings.WS4REDIS_SUBSCRIBER == 'websockets_helpers.FakeRedisSubscriber':
    logging.warning('using FakeRedis')
    RedisPublisher = FakeRedisPublisher
else:
    RedisPublisher = RealRedisPublisher
