from .models import ProjectMember
from home.notifications import notify_user


def notify_users(
    *,
    users,
    title,
    message,
    notification_type,
    project=None,
    task=None,
):
    for user in users:
        notify_user(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            project=project,
            task=task,
        )

def notify_project_members(
    *,
    project,
    title,
    message,
    notification_type="project",
    task=None,
    extra_users=None,
):
    users = set(
        ProjectMember.objects.filter(
            project=project,
            is_deleted=False
        ).values_list("user", flat=True)
    )

    if extra_users:
        users.update(extra_users)

    notify_users(
        users=users,
        title=title,
        message=message,
        notification_type=notification_type,
        project=project,
        task=task,
    )
