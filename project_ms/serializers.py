from rest_framework import serializers
from django.conf import settings
from .models import (
    Project,
    ProjectActivity,
    ProjectMember,
    Task,
    TaskComment,
    TaskActivity,
    Notification,
    Sprint,
    SprintMember,
    Milestone,
    MilestoneCriteria,
    AuditLog,
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

# 1
class SprintMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.name",
        read_only=True
    )

    class Meta:
        model = SprintMember
        fields = (
            "id",
            "user",
            "user_name",
            "role",
            "capacity_hours",
        )


class SprintMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SprintMember
        fields = ("user", "role", "capacity_hours")

# 2
class SprintMemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SprintMember
        fields = (
            "id",
            "user",
            "role",
            "capacity_hours",
        )


class SprintMemberBulkUpdateSerializer(serializers.Serializer):
    members = SprintMemberUpdateSerializer(many=True)

    def validate(self, attrs):
        roles = [m["role"] for m in attrs["members"]]

        if roles.count("scrum_master") != 1:
            raise serializers.ValidationError(
                "Exactly one Scrum Master is required."
            )

        if roles.count("product_owner") != 1:
            raise serializers.ValidationError(
                "Exactly one Product Owner is required."
            )

        return attrs


class SprintSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )
    total_capacity_hours = serializers.SerializerMethodField()

    class Meta:
        model = Sprint
        fields = (
            "id",
            "project",
            "project_name",
            "name",
            "sprint_number",
            "sprint_type",
            "goal",
            "start_date",
            "end_date",
            "duration_weeks",
            "working_days",
            "story_points_target",
            "status",
            "allow_task_overflow",
            "auto_close",
            "allow_scope_change",
            "freeze_when_active",
            "total_capacity_hours",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "total_capacity_hours",
        )

    def get_total_capacity_hours(self, obj):
        return sum(
            member.capacity_hours
            for member in obj.members.all()
        )


class SprintCreateSerializer(serializers.ModelSerializer):
    members = SprintMemberCreateSerializer(many=True)

    class Meta:
        model = Sprint
        fields = (
            "project",
            "name",
            "sprint_number",
            "sprint_type",
            "goal",
            "start_date",
            "duration_weeks",
            "working_days",
            "story_points_target",
            "allow_task_overflow",
            "auto_close",
            "allow_scope_change",
            "freeze_when_active",
            "members",
        )

    def validate(self, attrs):
        members = attrs.get("members", [])
        if not members:
            raise serializers.ValidationError(
                "At least one sprint member is required."
            )
        roles = [m["role"] for m in members]

        if "scrum_master" not in roles:
            raise serializers.ValidationError(
                "Sprint must have a Scrum Master."
            )

        if "product_owner" not in roles:
            raise serializers.ValidationError(
                "Sprint must have a Product Owner."
            )

        return attrs


class SprintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = (
            "name",
            "goal",
            "status",
            "start_date",
            "end_date",
            "working_days",
            "story_points_target",
            "allow_task_overflow",
            "auto_close",
            "allow_scope_change",
            "freeze_when_active",
        )


class MilestoneCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneCriteria
        fields = ("id", "title", "is_completed")


class MilestoneCreateSerializer(serializers.ModelSerializer):
    criteria = MilestoneCriteriaSerializer(many=True)

    class Meta:
        model = Milestone
        fields = (
            "project",
            "sprint",
            "title",
            "code",
            "description",
            "priority",
            "due_date",
            "owner",
            "status",
            "criteria",
        )

    def validate(self, attrs):
        if not attrs.get("criteria"):
            raise serializers.ValidationError(
                "At least one success criterion is required."
            )
        return attrs


class MilestoneSerializer(serializers.ModelSerializer):
    criteria = MilestoneCriteriaSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    sprint_name = serializers.CharField(source="sprint.name", read_only=True)

    class Meta:
        model = Milestone
        fields = "__all__"


class MilestoneUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = (
            "title",
            "description",
            "priority",
            "due_date",
            "owner",
            "status",
            "sprint",
        )


class MilestoneCriteriaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneCriteria
        fields = ("id", "is_completed")


class MilestoneDashboardSerializer(serializers.ModelSerializer):
    progress_percent = serializers.SerializerMethodField()
    completed_criteria = serializers.SerializerMethodField()
    total_criteria = serializers.SerializerMethodField()
    owner_name = serializers.CharField(
        source="owner.name",
        read_only=True
    )
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )
    sprint_name = serializers.CharField(
        source="sprint.name",
        read_only=True
    )

    class Meta:
        model = Milestone
        fields = (
            "id",
            "title",
            "code",
            "status",
            "priority",
            "due_date",
            "progress_percent",
            "completed_criteria",
            "total_criteria",
            "owner_name",
            "project_name",
            "sprint_name",
        )

    def get_total_criteria(self, obj):
        return obj.criteria.count()

    def get_completed_criteria(self, obj):
        return obj.criteria.filter(is_completed=True).count()

    def get_progress_percent(self, obj):
        total = self.get_total_criteria(obj)
        if total == 0:
            return 0
        return round(
            (self.get_completed_criteria(obj) / total) * 100
        )


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
    updated_by_name = serializers.CharField(
        source="updated_by.name",
        read_only=True
    )

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = (
            "id",
            "slug",
            "created_by",
            "updated_by",
            "assigned_at",
            "completed_at",
            "created_at",
            "updated_at",
        )

    def validate_assigned_to(self, user):
        if not user:
            return user

        # Role check
        if user.role not in ["staff", "team_leader", "freelancer"]:
            raise serializers.ValidationError(
                "Task can only be assigned to staff, team leader, or freelancer."
            )

        # Project membership check
        project = self.initial_data.get("project")
        if project:
            from project_ms.models import ProjectMember
            is_member = ProjectMember.objects.filter(
                project_id=project,
                user=user,
                is_deleted=False
            ).exists()

            if not is_member:
                raise serializers.ValidationError(
                    "User must be a member of the project."
                )

        return user


class TaskSprintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("sprint",)


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


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = AuditLog
        fields = "__all__"
        # read_only_fields = "__all__"
        

class SprintHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source="user.name",
        read_only=True
    )

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "action",
            "model_name",
            "old_data",
            "new_data",
            "performed_by_name",
            "created_at",
        )


class MilestoneHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source="user.name",
        read_only=True
    )

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "action",
            "model_name",
            "old_data",
            "new_data",
            "performed_by_name",
            "created_at",
        )


class UserOverviewSerializer(serializers.Serializer):
    # Basic info
    id = serializers.UUIDField()
    name = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()

    # Stats
    total_projects = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()

    # Lists
    task_assignments = serializers.ListField()
    active_projects = serializers.ListField()

    last_active = serializers.DateTimeField(allow_null=True)
