from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from project_ms.models import Notification


def notify_user(
    *,
    user,
    title,
    message,
    notification_type,
    project=None,
    task=None,
):
    """
    Single source of truth for notifications
    """

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        project=project,
        task=task,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "notify",
            "id": str(notification.id),
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "project_id": str(project.id) if project else None,
            "task_id": str(task.id) if task else None,
            "created_at": notification.created_at.isoformat(),
        }
    )

    return notification
