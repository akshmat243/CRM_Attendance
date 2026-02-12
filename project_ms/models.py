import uuid
from django.db import models
from permissions.models import SoftDeleteModel
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction

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
    code = models.CharField(max_length=50, unique=True, blank=True)

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
        
        if not self.code:
            with transaction.atomic():
                self.code = self.generate_unique_code()
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
    
    def generate_unique_code(self):
        base = slugify(self.name).upper().replace("-", "")[:4] or "PROJ"
        counter = 1

        while True:
            code = f"{base}-{counter:03d}"
            if not Project.objects.filter(code=code).exists():
                return code
            counter += 1

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
    
    
class Sprint(SoftDeleteModel):
    STATUS_CHOICES = (
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
    )

    SPRINT_TYPE_CHOICES = (
        ("development", "Development"),
        ("bugfix", "Bug Fix"),
        ("release", "Release"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="sprints"
    )

    name = models.CharField(max_length=255)
    sprint_number = models.CharField(max_length=50)
    sprint_type = models.CharField(
        max_length=20,
        choices=SPRINT_TYPE_CHOICES
    )

    goal = models.TextField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField()
    duration_weeks = models.PositiveIntegerField(default=2)

    working_days = models.JSONField(default=list)

    story_points_target = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
        db_index=True
    )

    # Sprint settings
    allow_task_overflow = models.BooleanField(default=False)
    auto_close = models.BooleanField(default=True)
    allow_scope_change = models.BooleanField(default=False)
    freeze_when_active = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_sprints"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["start_date", "end_date"]),
        ]
        unique_together = ("project", "sprint_number")
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.project.name} - {self.sprint_number}"


class SprintMember(models.Model):
    ROLE_CHOICES = (
        ("scrum_master", "Scrum Master"),
        ("product_owner", "Product Owner"),
        ("developer", "Developer"),
        ("qa", "QA Engineer"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sprint = models.ForeignKey(
        "Sprint",
        on_delete=models.CASCADE,
        related_name="members"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    capacity_hours = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("sprint", "user")

    def __str__(self):
        return f"{self.user} - {self.role}"


class Milestone(SoftDeleteModel):
    STATUS_CHOICES = (
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("completed", "Completed"),
    )

    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="milestones"
    )

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milestones"
    )

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    description = models.TextField(blank=True)

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    due_date = models.DateField()

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_milestones"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="not_started",
        db_index=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_milestones"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["priority"]),
        ]
        ordering = ["due_date"]
        unique_together = ("project", "title")

    def __str__(self):
        return self.title


class MilestoneCriteria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    milestone = models.ForeignKey(
        "Milestone",
        on_delete=models.CASCADE,
        related_name="criteria"
    )

    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


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
    
    position = models.PositiveIntegerField(default=0, db_index=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)


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
    
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_updated"
    )
    
    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks"
    )

    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_date", "status"]),
            models.Index(fields=["sprint", "status"]),
            models.Index(fields=["milestone", "status"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            old = Task.objects.filter(pk=self.pk).first()

            if old and old.assigned_to != self.assigned_to:
                self.assigned_at = timezone.now()

            if old and old.status != "done" and self.status == "done":
                self.completed_at = timezone.now()

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
        ("milestone", "Milestone"),
        ("sprint", "Sprint"),
        
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
    
    class Meta:
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} → {self.user}"


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("status_change", "Status Change"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)

    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}"
