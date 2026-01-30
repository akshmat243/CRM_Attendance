from .base_views import ProtectedModelViewSet
from .models import Project, ProjectMember, Task, TaskComment, TaskActivity, ProjectActivity, Notification
from .serializers import (
    ProjectSerializer,
    ProjectMemberSerializer,
    TaskSerializer,
    TaskCommentSerializer,
    TaskActivitySerializer,
    ProjectActivitySerializer,
    NotificationSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskKanbanUpdateSerializer



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

    allowed_roles = ["super_user", "admin", "team_leader"]
    read_roles = ["super_user", "admin", "team_leader"]

    def get_queryset(self):
        return ProjectMember.objects.filter(
            project__project_members__user=self.request.user
        )


class TaskViewSet(ProtectedModelViewSet):
    serializer_class = TaskSerializer

    allowed_roles = ["super_user", "admin", "team_leader", "staff"]
    read_roles = ["super_user", "admin", "team_leader", "staff", "freelancer", "it_staff"]

    def get_queryset(self):
        user = self.request.user

        qs = Task.objects.select_related(
            "project",
            "assigned_to",
            "created_by"
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
