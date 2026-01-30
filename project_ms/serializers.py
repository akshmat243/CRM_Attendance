from rest_framework import serializers
from django.conf import settings
from .models import (
    Project,
    ProjectActivity,
    ProjectMember,
    Task,
    TaskComment,
    TaskActivity,
    Notification
)

User = settings.AUTH_USER_MODEL

class ProjectSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.name",
        read_only=True
    )

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = (
            "id",
            "slug",
            "created_by",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        return super().create(validated_data)

class ProjectMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.name",
        read_only=True
    )
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )

    class Meta:
        model = ProjectMember
        fields = "__all__"
        read_only_fields = (
            "id",
            "assigned_by",
            "assigned_at",
        )

    def validate_user(self, user):
        # Optional safety: ensure only staff/freelancer assigned
        if user.role not in ["staff", "team_leader", "freelancer"]:
            raise serializers.ValidationError(
                "Only staff, team leaders, or freelancers can be assigned to projects."
            )
        return user

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["assigned_by"] = request.user
        return super().create(validated_data)

class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )
    assigned_to_name = serializers.CharField(
        source="assigned_to.name",
        read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.name",
        read_only=True
    )

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = (
            "id",
            "slug",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate_assigned_to(self, user):
        if user and user.role not in ["staff", "team_leader", "freelancer"]:
            raise serializers.ValidationError(
                "Task can only be assigned to staff, team leader, or freelancer."
            )
        return user

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        return super().create(validated_data)


class TaskCommentSerializer(serializers.ModelSerializer):
    commented_by_name = serializers.CharField(
        source="commented_by.name",
        read_only=True
    )

    class Meta:
        model = TaskComment
        fields = "__all__"
        read_only_fields = (
            "id",
            "commented_by",
            "created_at",
        )

    def create(self, validated_data):
        validated_data["commented_by"] = self.context["request"].user
        return super().create(validated_data)


class TaskActivitySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source="performed_by.name",
        read_only=True
    )
    task_title = serializers.CharField(
        source="task.title",
        read_only=True
    )

    class Meta:
        model = TaskActivity
        fields = "__all__"
        # read_only_fields = "__all__"

class TaskKanbanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["status"]

    def validate_status(self, new_status):
        task = self.instance
        user = self.context["request"].user

        from .kanban import TASK_STATUS_FLOW
        from .kanban_permissions import ROLE_ALLOWED_STATUS_CHANGE

        # Check role permission
        if new_status not in ROLE_ALLOWED_STATUS_CHANGE.get(user.role, []):
            raise serializers.ValidationError(
                "You are not allowed to move task to this status."
            )

        # Check flow rule
        allowed_next = TASK_STATUS_FLOW.get(task.status, [])
        if new_status not in allowed_next:
            raise serializers.ValidationError(
                f"Invalid transition from '{task.status}' to '{new_status}'."
            )

        return new_status

class ProjectActivitySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source="performed_by.name",
        read_only=True
    )

    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )

    class Meta:
        model = ProjectActivity
        fields = "__all__"
        # read_only_fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )
    task_title = serializers.CharField(
        source="task.title",
        read_only=True
    )

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = (
            "id",
            "user",
            "created_at",
        )

from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()

    total_tasks = serializers.IntegerField()
    todo_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    review_tasks = serializers.IntegerField()
    done_tasks = serializers.IntegerField()

    overdue_tasks = serializers.IntegerField()

class ActiveTaskListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "status",
            "priority",
            "project_name",
        )

class UpcomingDeadlineSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )
    days_left = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "due_date",
            "days_left",
            "project_name",
        )
        
class TeamWorkloadSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    name = serializers.CharField()
    role = serializers.CharField()
    task_count = serializers.IntegerField()
    workload_percent = serializers.IntegerField()