from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from home.notifications import notify_user
from .utils import extract_mentions, log_audit, serialize_instance
from .models import (
    Project,
    ProjectActivity,
    ProjectMember,
    Task,
    TaskComment,
    TaskActivity,
    Notification,
    MilestoneCriteria,
    Milestone,
    Sprint,
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
    # if instance.assigned_to:
    #     notify_user(
    #         user=instance.assigned_to,
    #         title="Task assigned",
    #         message=f"You were assigned task '{instance.title}'",
    #         notification_type="task",
    #         project=instance.project,
    #         task=instance
    #     )


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
    # notify_user(
    #     user=instance.assigned_to if instance.assigned_to else instance.created_by,
    #     title="Task Created",
    #     message=f"Task '{instance.title}' has been created.",
    #     notification_type="task",
    #     project=instance.project,
    #     task=instance,
    # )

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
            exclude_user=instance.assigned_to if instance.assigned_to else instance.created_by
        )
    notify_user(
        user=instance.assigned_to if instance.assigned_to else instance.created_by,
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
        
        
        
@receiver(post_save, sender=Task)
def auto_close_sprint_on_task_done(sender, instance, **kwargs):
    sprint = instance.sprint

    if not sprint:
        return

    # Only if auto-close enabled
    if not sprint.auto_close:
        return

    # Only act when task is DONE
    if instance.status != "done":
        return

    # Check if any task still not done
    pending_exists = Task.objects.filter(
        sprint=sprint,
        is_deleted=False
    ).exclude(status="done").exists()

    if not pending_exists:
        sprint.status = "completed"
        sprint.save(update_fields=["status"])
        ProjectActivity.objects.create(
            project=sprint.project,
            action="sprint_completed",
            performed_by=instance.created_by,
            description=f"Sprint '{sprint.name}' was auto-closed as all tasks are done."
        )
        
@receiver(post_save, sender=MilestoneCriteria)
def auto_complete_milestone_on_criteria(sender, instance, **kwargs):
    milestone = instance.milestone

    if milestone.status == "completed":
        return

    total = milestone.criteria.count()
    completed = milestone.criteria.filter(is_completed=True).count()

    if total > 0 and total == completed:
        milestone.status = "completed"
        milestone.save(update_fields=["status"])
        ProjectActivity.objects.create(
            project=milestone.project,
            action="milestone_completed",
            performed_by=instance.updated_by,
            description=f"Milestone '{milestone.name}' was auto-completed as all criteria are met."
        )

@receiver(post_save, sender=Milestone)
def milestone_notifications(sender, instance, created, **kwargs):
    if created:
        return

    # Blocked
    if instance.status == "blocked":
        notify_project_members(
            project=instance.project,
            title="Milestone Blocked",
            message=f"Milestone '{instance.title}' is blocked.",
            notification_type="milestone",
            extra_users=[instance.owner] if instance.owner else None
        )

    # Completed
    if instance.status == "completed":
        notify_project_members(
            project=instance.project,
            title="Milestone Completed",
            message=f"Milestone '{instance.title}' has been completed.",
            notification_type="project",
            extra_users=[instance.owner] if instance.owner else None
        )

@receiver(post_save, sender=Task)
def task_assignment_notification(sender, instance, created, **kwargs):
    if instance.assigned_to:
        notify_user(
            user=instance.assigned_to,
            title="Task Assigned",
            message=f"You have been assigned task '{instance.title}'.",
            notification_type="task",
            project=instance.project,
            task=instance
        )

@receiver(post_save, sender=TaskComment)
def task_comment_mentions(sender, instance, created, **kwargs):
    if not created:
        return

    mentioned_users = extract_mentions(instance.comment)

    for user in mentioned_users:
        # Don't notify self
        if user == instance.user:
            continue

        notify_user(
            user=user,
            title="You were mentioned",
            message=(
                f"{instance.user.name or instance.user.username} "
                f"mentioned you in a comment."
            ),
            notification_type="comment",
            project=instance.task.project,
            task=instance.task
        )


@receiver(pre_save)
def capture_old_data(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._old_data = serialize_instance(old_instance)
    except sender.DoesNotExist:
        instance._old_data = None

TRACKED_MODELS = (
    Project,
    Task,
    Sprint,
    Milestone,
    TaskComment,
)


@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    # Ignore system models
    if sender not in TRACKED_MODELS:
        return

    user = getattr(instance, "updated_by", None) or getattr(instance, "created_by", None)

    if created:
        log_audit(
            user=user,
            action="create",
            instance=instance,
            new_data=serialize_instance(instance)
        )
    else:
        log_audit(
            user=user,
            action="update",
            instance=instance,
            old_data=getattr(instance, "_old_data", None),
            new_data=serialize_instance(instance)
        )
