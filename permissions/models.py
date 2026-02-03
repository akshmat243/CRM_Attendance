import uuid
from django.db import models


class AppModel(models.Model):
    """
    Represents a model in an app (e.g., project.Task)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    app_label = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.app_label}.{self.model_name}"


class PermissionType(models.Model):
    """
    CRUD permission types
    """
    code = models.CharField(max_length=50, unique=True)  # view, add, change, delete
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RoleModelPermission(models.Model):
    """
    Maps Role → Model → Permission
    """
    ROLES = (
        ("super_user", "Super User"),
        ("admin", "Admin"),
        ("team_leader", "Team Leader"),
        ("staff", "Staff"),
        ("freelancer", "Freelancer"),
        ("it_staff", "IT Staff"),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    role = models.CharField(max_length=20, choices=ROLES, default="staff")
    app_model = models.ForeignKey(AppModel, on_delete=models.CASCADE)
    permission = models.ForeignKey(PermissionType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("role", "app_model", "permission")

    def __str__(self):
        return f"{self.role} | {self.app_model} | {self.permission}"






from django.db import models
from django.utils.timezone import now


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        "home.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_%(class)s_set"
    )

    objects = SoftDeleteManager()      # default
    all_objects = models.Manager()     # includes deleted

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        from project_ms.utils import log_audit, serialize_instance

        log_audit(
            user=user,
            action="delete",
            instance=self,
            old_data=serialize_instance(self),
        )
        
        self.is_deleted = True
        self.deleted_at = now()
        self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])
