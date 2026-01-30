import uuid
from django.db import models
from permissions.models import SoftDeleteModel
from django.conf import settings
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class Project(SoftDeleteModel):
    STATUS_CHOICES = (
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
        db_index=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="projects_created"
    )

    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProjectMember(SoftDeleteModel):
    ROLE_CHOICES = (
        ("super_user", "Super User"),
        ("admin", "Admin"),
        ("team_leader", "Team Leader"),
        ("staff", "Staff"),
        ("freelancer", "Freelancer"),
        ("it_staff", "IT Staff"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_members"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_projects"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_members"
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")
        indexes = [
            models.Index(fields=["project", "user"]),
        ]

    def __str__(self):
        return f"{self.user} → {self.project} ({self.role})"

class Task(SoftDeleteModel):
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    STATUS_CHOICES = (
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
        ("blocked", "Blocked"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned",
        db_index=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium",
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="todo", 
        db_index=True
    )

    due_date = models.DateField(null=True, blank=True, db_index=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tasks_created"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_date", "status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.title)}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class TaskComment(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    comment = models.TextField()

    commented_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.task}"


class TaskActivity(SoftDeleteModel):
    ACTION_CHOICES = (
        ("created", "Created"),
        ("updated", "Updated"),
        ("status_changed", "Status Changed"),
        ("assigned", "Assigned"),
        ("commented", "Commented"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    action = models.CharField(max_length=30, choices=ACTION_CHOICES)

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.action} → {self.task}"

class ProjectActivity(SoftDeleteModel):
    ACTION_CHOICES = (
        ("created", "Created"),
        ("updated", "Updated"),
        ("member_added", "Member Added"),
        ("member_removed", "Member Removed"),
        ("task_created", "Task Created"),
        ("task_updated", "Task Updated"),
        ("status_changed", "Status Changed"),
        ("commented", "Commented"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    action = models.CharField(max_length=30, choices=ACTION_CHOICES)

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.project.name}"

class Notification(SoftDeleteModel):
    NOTIFICATION_TYPE = (
        ("project", "Project"),
        ("task", "Task"),
        ("comment", "Comment"),
        ("system", "System"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.title} → {self.user}"
