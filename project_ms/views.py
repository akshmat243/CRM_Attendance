from .base_views import ProtectedModelViewSet
from .models import Project, ProjectMember, Task, TaskComment, TaskActivity, ProjectActivity, Notification, SprintMember, Sprint, MilestoneCriteria, AuditLog, Milestone
from .utils import calculate_end_date
from .serializers import (
    ProjectSerializer,
    ProjectMemberSerializer,
    TaskSerializer,
    TaskCommentSerializer,
    TaskActivitySerializer,
    ProjectActivitySerializer,
    NotificationSerializer,
    SprintSerializer,
    SprintCreateSerializer,
    SprintUpdateSerializer,
    SprintMemberBulkUpdateSerializer,
    TaskSprintUpdateSerializer,
    MilestoneSerializer,
    MilestoneCreateSerializer,
    MilestoneCriteriaUpdateSerializer,
    AuditLogSerializer,
    TaskKanbanUpdateSerializer,
    MilestoneCriteriaUpdateSerializer,
)
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskKanbanUpdateSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.db.models import Q


@method_decorator(cache_page(60), name="list")
class ProjectViewSet(ProtectedModelViewSet):
    serializer_class = ProjectSerializer

    allowed_roles = ["super_user", "admin", "team_leader"]
    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]

    def get_queryset(self):
        user = self.request.user

        qs = Project.objects.select_related(
            "created_by"
        ).prefetch_related(
            "project_members__user"
        )

        # Super user sees everything
        if user.role in ["super_user", "admin"]:
            return qs

        # All other users ONLY see projects they are assigned to
        return qs.filter(
            project_members__user=user,
            project_members__is_deleted=False,   # if soft delete is enabled
            is_deleted=False
        ).distinct()


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectMemberViewSet(ProtectedModelViewSet):
    serializer_class = ProjectMemberSerializer
    queryset = ProjectMember.objects.select_related(
        "project",
        "user",
        "assigned_by"
    )

    allowed_roles = ["super_user", "admin", "team_leader"]
    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer"]

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.filter(is_deleted=False)

        project_id = self.request.query_params.get("project")

        # 🔹 Filter by project if provided
        if project_id:
            project = get_object_or_404(
                Project,
                id=project_id,
                is_deleted=False
            )

            # 🔐 Access control
            if user.role not in ["super_user", "admin"]:
                is_member = ProjectMember.objects.filter(
                    project=project,
                    user=user,
                    is_deleted=False
                ).exists()

                if not is_member:
                    return ProjectMember.objects.none()

            qs = qs.filter(project=project)

        # 🔹 Non-admin users see only their projects
        if user.role not in ["super_user", "admin"]:
            qs = qs.filter(
                Q(user=user) |
                Q(project__project_members__user=user)
            ).distinct()

        return qs

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class SprintViewSet(ProtectedModelViewSet):
    serializer_class = SprintSerializer

    allowed_roles = ["super_user", "admin", "team_leader"]
    read_roles = [
        "super_user",
        "admin",
        "team_leader",
        "staff",
        "freelancer",
        "it_staff",
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return SprintCreateSerializer
        if self.action in ["update", "partial_update"]:
            return SprintUpdateSerializer
        return SprintSerializer

    def get_queryset(self):
        user = self.request.user

        qs = Sprint.objects.select_related(
            "project",
            "created_by"
        ).prefetch_related(
            "members"
        ).filter(is_deleted=False)

        if user.role in ["super_user", "admin"]:
            return qs

        return qs.filter(
            project__project_members__user=user,
            project__project_members__is_deleted=False
        ).distinct()

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        members_data = serializer.validated_data.pop("members")

        # Auto end-date calculation
        start_date = serializer.validated_data["start_date"]
        duration = serializer.validated_data["duration_weeks"]
        working_days = serializer.validated_data.get("working_days", [])

        end_date = calculate_end_date(
            start_date,
            duration,
            working_days
        )

        sprint = serializer.save(
            created_by=user,
            end_date=end_date
        )

        # Validate sprint members belong to project
        project_member_ids = set(
            ProjectMember.objects.filter(
                project=sprint.project,
                is_deleted=False
            ).values_list("user_id", flat=True)
        )

        for member in members_data:
            if member["user"].id not in project_member_ids:
                raise ValidationError(
                    f"{member['user']} is not a member of this project."
                )

            SprintMember.objects.create(
                sprint=sprint,
                user=member["user"],
                role=member["role"],
                capacity_hours=member["capacity_hours"],
            )
            
    # PUT /api/sprints/{sprint_id}/update-members/
    @action(
        detail=True,
        methods=["put"],
        url_path="update-members"
    )
    @transaction.atomic
    def update_members(self, request, pk=None):
        sprint = self.get_object()

        serializer = SprintMemberBulkUpdateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        members_data = serializer.validated_data["members"]

        # Project members check
        project_member_ids = set(
            ProjectMember.objects.filter(
                project=sprint.project,
                is_deleted=False
            ).values_list("user_id", flat=True)
        )

        SprintMember.objects.filter(
            sprint=sprint
        ).delete()

        for member in members_data:
            if member["user"].id not in project_member_ids:
                raise ValidationError(
                    f"{member['user']} is not a project member."
                )

            SprintMember.objects.create(
                sprint=sprint,
                user=member["user"],
                role=member["role"],
                capacity_hours=member["capacity_hours"],
            )

        return Response({
            "message": "Sprint members updated successfully."
        })


class MilestoneViewSet(ProtectedModelViewSet):
    serializer_class = MilestoneSerializer

    allowed_roles = ["super_user", "admin", "team_leader"]
    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]

    def get_serializer_class(self):
        if self.action == "create":
            return MilestoneCreateSerializer
        return MilestoneSerializer
    
    def get_queryset(self):
        user = self.request.user

        qs = Milestone.objects.select_related(
            "project",
            "created_by"
        ).prefetch_related(
            "criteria"
        ).filter(is_deleted=False)

        if user.role in ["super_user", "admin"]:
            return qs

        return qs.filter(
            project__project_members__user=user,
            project__project_members__is_deleted=False
        ).distinct()

    @transaction.atomic
    def perform_create(self, serializer):
        criteria_data = serializer.validated_data.pop("criteria")

        milestone = serializer.save(
            created_by=self.request.user
        )

        for c in criteria_data:
            MilestoneCriteria.objects.create(
                milestone=milestone,
                **c
            )
    
    @action(
        detail=True,
        methods=["put"],
        url_path="update-criteria"
    )
    @transaction.atomic
    def update_criteria(self, request, pk=None):
        milestone = self.get_object()

        serializer = MilestoneCriteriaUpdateSerializer(
            data=request.data,
            many=True
        )
        serializer.is_valid(raise_exception=True)

        criteria_map = {
            c.id: c for c in milestone.criteria.all()
        }

        for item in serializer.validated_data:
            criteria = criteria_map.get(item["id"])
            if criteria:
                criteria.is_completed = item["is_completed"]
                criteria.save(update_fields=["is_completed"])

        # 🔥 AUTO UPDATE MILESTONE STATUS
        total = milestone.criteria.count()
        completed = milestone.criteria.filter(
            is_completed=True
        ).count()

        if completed == 0:
            milestone.status = "not_started"
        elif completed < total:
            milestone.status = "in_progress"
        else:
            milestone.status = "completed"

        milestone.save(update_fields=["status"])

        return Response({
            "message": "Milestone criteria updated successfully.",
            "status": milestone.status,
            "completed": completed,
            "total": total,
        })


class TaskViewSet(ProtectedModelViewSet):
    serializer_class = TaskSerializer

    allowed_roles = ["super_user", "admin", "team_leader", "staff"]
    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]

    def get_queryset(self):
        user = self.request.user

        qs = Task.objects.select_related(
            "project",
            "assigned_to",
            "created_by",
            "sprint",
            "milestone"
        ).filter(
            is_deleted=False
        )

        # Super users & admins see everything
        if user.role in ["super_user", "admin"]:
            return qs

        # Team leaders see all tasks in their projects
        if user.role == "team_leader":
            return qs.filter(
                project__project_members__user=user,
                project__project_members__is_deleted=False
            ).distinct()

        # Staff / freelancer / IT staff see ONLY their tasks
        return qs.filter(
            assigned_to=user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    # 🔥 KANBAN MOVE ENDPOINT
    @action(detail=True, methods=["patch"], url_path="move")
    def move_task(self, request, pk=None):
        task = self.get_object()

        serializer = TaskKanbanUpdateSerializer(
            task,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Task moved successfully", "status": task.status},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=["post"], url_path="restore")
    def restore_task(self, request, pk=None):
        task = self.get_object()

        if request.user.role not in ["super_user", "admin", "team_leader"]:
            return Response(
                {"detail": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )

        task.restore()
        return Response({"message": "Task restored successfully"})
    
    @action(detail=True, methods=["patch"], url_path="assign-sprint")
    def assign_sprint(self, request, pk=None):
        task = self.get_object()

        serializer = TaskSprintUpdateSerializer(
            task,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        sprint = serializer.validated_data.get("sprint")

        # Safety check: sprint must belong to same project
        if sprint and sprint.project_id != task.project_id:
            raise PermissionDenied(
                "Sprint does not belong to this task's project."
            )

        serializer.save()
        return Response({
            "message": "Task sprint updated successfully."
        })

    # 🔹 REMOVE TASK FROM SPRINT
    @action(detail=True, methods=["patch"], url_path="remove-sprint")
    def remove_sprint(self, request, pk=None):
        task = self.get_object()
        task.sprint = None
        task.save(update_fields=["sprint"])
        return Response({
            "message": "Task removed from sprint."
        })
    
    @action(detail=True, methods=["patch"])
    def update_position(self, request, pk=None):
        task = self.get_object()
        task.position = request.data.get("position", task.position)
        task.save(update_fields=["position"])
        return Response({"message": "Position updated"})



class SprintTaskListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, sprint_id):
        user = request.user

        qs = Task.objects.select_related(
            "assigned_to",
            "project"
        ).filter(
            sprint_id=sprint_id,
            is_deleted=False
        )

        if user.role in ["super_user", "admin"]:
            tasks = qs

        elif user.role == "team_leader":
            tasks = qs.filter(
                project__project_members__user=user
            ).distinct()

        else:
            tasks = qs.filter(assigned_to=user)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskCommentViewSet(ProtectedModelViewSet):
    serializer_class = TaskCommentSerializer

    allowed_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]
    read_roles = allowed_roles

    def get_queryset(self):
        return TaskComment.objects.filter(
            task__project__project_members__user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(commented_by=self.request.user)


class TaskActivityViewSet(ProtectedModelViewSet):
    serializer_class = TaskActivitySerializer
    http_method_names = ["get"]

    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]

    def get_queryset(self):
        user = self.request.user

        if user.role in ["super_user", "admin"]:
            return TaskActivity.objects.all()

        return TaskActivity.objects.filter(
            task__project__project_members__user=user
        )


class ProjectActivityViewSet(ProtectedModelViewSet):
    serializer_class = ProjectActivitySerializer
    http_method_names = ["get"]

    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]

    def get_queryset(self):
        user = self.request.user

        if user.role in ["super_user", "admin"]:
            return ProjectActivity.objects.select_related(
                "project", "performed_by"
            )

        return ProjectActivity.objects.filter(
            project__project_members__user=user
        ).select_related("project", "performed_by")


class NotificationViewSet(ProtectedModelViewSet):
    serializer_class = NotificationSerializer

    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]
    allowed_roles = read_roles

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).select_related("project", "task")


    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    
    # PATCH /api/notifications/{id}/mark-read/
    @action(detail=True, methods=["patch"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response({
            "message": "Notification marked as read."
        })
    
    @action(detail=False, methods=["patch"], url_path="mark-all-read")
    def mark_all_read(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False,
            is_deleted=False
        ).update(is_read=True)

        return Response({
            "message": "All notifications marked as read."
        })


class NotificationUnreadCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False,
            is_deleted=False
        ).count()

        return Response({
            "unread_count": count
        })


class AuditLogViewSet(ProtectedModelViewSet):
    serializer_class = AuditLogSerializer
    read_roles = ["super_user", "admin"]

    def get_queryset(self):
        return AuditLog.objects.select_related(
            "user"
        ).order_by("-created_at")
