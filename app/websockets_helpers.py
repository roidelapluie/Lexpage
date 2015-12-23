from ws4redis.subscriber import RedisSubscriber
from ws4redis.publisher import RedisPublisher
import fakeredis


class FakeRedisSubscriber(RedisSubscriber):
    def __init__(self, connection):
        super(FakeRedisSubscriber, self).__init__(fakeredis.FakeStrictRedis())
        print('Started %s' % self)

    def get_file_descriptor(self):
        return None

class FakeRedisPublisher(RedisPublisher):
    def __init__(self, **kwargs):
        """
        Initialize the channels for publishing messages through the message queue.
        """
        connection = fakeredis.FakeStrictRedis()
        super(RedisPublisher, self).__init__(connection)
        for key in self._get_message_channels(**kwargs):
            self._publishers.add(key)
