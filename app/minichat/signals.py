from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

@receiver(post_save, sender=Message)
def send_minichat_update_message(sender, **kwargs):
    redis_publisher = RedisPublisher(facility='minichat', broadcast=True)
    redis_message = RedisMessage('new-message')
    redis_publisher.publish_message(redis_message)

