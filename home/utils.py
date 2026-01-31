from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
User = get_user_model()

def send_notification_to_user(user_id, title, message, data=None):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "notify",
            "title": title,
            "message": message,
            "data": data or {}
        }
    )


def send_notification_to_users(user_ids, title, message):
    channel_layer = get_channel_layer()

    for user_id in user_ids:
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "notify",
                "title": title,
                "message": message
            }
        )


def send_notification_to_role(role_name, title, message):
    users = User.objects.filter(role__name=role_name)

    for user in users:
        send_notification_to_user(user.id, title, message)



def send_notification_to_all(title, message):
    for user in User.objects.all():
        send_notification_to_user(user.id, title, message)