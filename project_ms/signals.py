from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from home.notifications import notify_user
from .models import (
    Project,
    ProjectActivity,
    ProjectMember,
    Task,
    TaskComment,
    TaskActivity,
    Notification
)

@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):
    if created:
        TaskActivity.objects.create(
            task=instance,
            action="created",
            performed_by=instance.created_by,
            description=f"Task '{instance.title}' was created."
        )
    notify_user(
        user=instance.created_by,
        title="Task Created",
        message=f"Task '{instance.title}' has been created.",
        notification_type="task",
        project=instance.project,
        task=instance,
    )

@receiver(pre_save, sender=Task)
def task_updated(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_task = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return

    # STATUS CHANGE
    if old_task.status != instance.status:
        TaskActivity.objects.create(
            task=instance,
            action="status_changed",
            performed_by=instance.created_by,
            description=f"Status changed from '{old_task.status}' to '{instance.status}'."
        )

    # ASSIGNMENT CHANGE
    if old_task.assigned_to != instance.assigned_to:
        TaskActivity.objects.create(
            task=instance,
            action="assigned",
            performed_by=instance.created_by,
            description=f"Task assigned to {instance.assigned_to}."
        )
    notify_user(
        user=instance.created_by,
        title="Task Updated",
        message=f"Task '{instance.title}' has been updated.",
        notification_type="task",
        project=instance.project,
        task=instance,
    )

@receiver(post_save, sender=TaskComment)
def task_commented(sender, instance, created, **kwargs):
    if created:
        TaskActivity.objects.create(
            task=instance.task,
            action="commented",
            performed_by=instance.commented_by,
            description="A new comment was added."
        )
    notify_user(
        user=instance.commented_by,
        title="New Comment Added",
        message=f"A new comment was added to task '{instance.task.title}'.",
        notification_type="comment",
        project=instance.task.project,
        task=instance.task,
    )

@receiver(post_save, sender=ProjectMember)
def project_member_added(sender, instance, created, **kwargs):
    if created:
        ProjectActivity.objects.create(
            project=instance.project,
            action="member_added",
            performed_by=instance.assigned_by,
            description=(
                f"{instance.user} was added to project "
                f"'{instance.project.name}' as {instance.role}."
            )
        )
    
    notify_user(
        user=instance.user,
        title="Added to Project",
        message=f"You were added to project '{instance.project.name}' as {instance.role}.",
        notification_type="project",
        project=instance.project,
    )


@receiver(post_save, sender=Project)
def project_created(sender, instance, created, **kwargs):
    if created:
        ProjectActivity.objects.create(
            project=instance,
            action="created",
            performed_by=instance.created_by,
            description=f"Project '{instance.name}' was created."
        )

# @receiver(post_save, sender=ProjectMember)
# def project_member_added(sender, instance, created, **kwargs):
#     if created:
#         ProjectActivity.objects.create(
#             project=instance.project,
#             action="member_added",
#             performed_by=instance.assigned_by,
#             description=(
#                 f"{instance.user} joined project as {instance.role}."
#             )
#         )

@receiver(post_save, sender=Task)
def project_task_created(sender, instance, created, **kwargs):
    if created:
        ProjectActivity.objects.create(
            project=instance.project,
            action="task_created",
            performed_by=instance.created_by,
            description=f"Task '{instance.title}' was created."
        )
    notify_user(
        user=instance.created_by,
        title="Task Created",
        message=f"Task '{instance.title}' has been created.",
        notification_type="task",
        project=instance.project,
        task=instance,
    )

@receiver(pre_save, sender=Task)
def project_task_status_changed(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Task.objects.filter(pk=instance.pk).first()
    if not old:
        return

    if old.status != instance.status:
        ProjectActivity.objects.create(
            project=instance.project,
            action="status_changed",
            performed_by=instance.created_by,
            description=(
                f"Task '{instance.title}' moved from "
                f"{old.status} → {instance.status}"
            )
        )
    notify_user(
        user=instance.created_by,
        title="Task Updated",
        message=f"Task '{instance.title}' has been updated.",
        notification_type="task",
        project=instance.project,
        task=instance,
    )

def notify_project_members(project, title, message, exclude_user=None):
    members = project.project_members.select_related("user")

    for member in members:
        if exclude_user and member.user == exclude_user:
            continue

        Notification.objects.create(
            user=member.user,
            title=title,
            message=message,
            notification_type="project",
            project=project
        )
        notify_user(
            user=member.user,
            title=title,
            message=message,
            notification_type="project",
            project=project,
            task=None,
        )

@receiver(post_save, sender=Task)
def notify_task_created(sender, instance, created, **kwargs):
    if created:
        notify_project_members(
            project=instance.project,
            title="New Task Created",
            message=f"Task '{instance.title}' was created.",
            exclude_user=instance.created_by
        )
    notify_user(
        user=instance.created_by,
        title="Task Created",
        message=f"Task '{instance.title}' has been created.",
        notification_type="task",
        project=instance.project,
        task=instance,
    )

@receiver(pre_save, sender=Task)
def notify_task_assignment(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Task.objects.filter(pk=instance.pk).first()
    if not old:
        return

    if old.assigned_to != instance.assigned_to and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to,
            title="Task Assigned",
            message=f"You were assigned '{instance.title}'",
            notification_type="task",
            project=instance.project,
            task=instance
        )

        notify_user(
            user=instance.assigned_to,
            title="New Task Assigned",
            message=f"Task '{instance.title}' was assigned to you.",
            notification_type="task",
            project=instance.project,
            task=instance,
        )


@receiver(post_save, sender=TaskComment)
def notify_task_comment(sender, instance, created, **kwargs):
    if created and instance.task.assigned_to:
        Notification.objects.create(
            user=instance.task.assigned_to,
            title="New Comment on Task",
            message="A new comment was added to your task.",
            notification_type="comment",
            project=instance.task.project,
            task=instance.task
        )
        notify_user(
            user=instance.task.assigned_to,
            title="New Comment on Your Task",
            message=f"A new comment was added to task '{instance.task.title}'.",
            notification_type="comment",
            project=instance.task.project,
            task=instance.task,
        )