from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

@receiver(post_delete, sender=Notification)
@receiver(post_save, sender=Notification)
def send_notification_update_message(sender, **kwargs):
    notification = kwargs.get('instance')
    redis_publisher = RedisPublisher(facility='notifications', users=[notification.recipient])
    redis_message = RedisMessage('notification-changed')
    redis_publisher.publish_message(redis_message)

