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
    SprintHistorySerializer,
    MilestoneHistorySerializer,
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
from django.db.models import Q, Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
User = get_user_model()
from home.serializers import UserSerializer



class UserViewSet(ProtectedModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    allowed_roles = ["super_user", "admin"]
    read_roles = ["super_user", "admin"]

    @action(detail=True, methods=["get"], url_path="overview")
    def overview(self, request, pk=None):
        user = get_object_or_404(User, id=pk)

        # 🔹 Projects
        project_memberships = ProjectMember.objects.filter(
            user=user,
            is_deleted=False
        ).select_related("project")

        active_projects = [
            {
                "id": pm.project.id,
                "name": pm.project.name,
                "role": pm.role,
            }
            for pm in project_memberships
        ]

        # 🔹 Tasks
        tasks = Task.objects.filter(
            assigned_to=user,
            is_deleted=False
        ).select_related("project")

        task_assignments = [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "project_slug": t.project.slug,
                "project_name": t.project.name,
            }
            for t in tasks
        ]

        completed_tasks = tasks.filter(status="done").count()
        pending_tasks = tasks.exclude(status="done").count()

        data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,

            "total_projects": project_memberships.count(),
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,

            "task_assignments": task_assignments,
            "active_projects": active_projects,

            "last_active": user.last_login,
        }

        return Response(data)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class TeamOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role not in ["super_user", "admin"]:
            return Response({"detail": "Forbidden"}, status=403)

        # 🔹 MEMBERS
        members = User.objects.filter(
            role__in=["team_leader", "staff", "freelancer", "it_staff"]
        )

        rows = []

        for m in members:
            project_names = ProjectMember.objects.filter(
                user=m,
                is_deleted=False
            ).values_list("project__name", flat=True)

            task_count = Task.objects.filter(
                assigned_to=m,
                is_deleted=False
            ).count()

            rows.append({
                "id": m.id,
                "name": m.name,
                "role": m.role.replace("_", " ").title(),
                "email": m.email,
                "projects": list(project_names),
                "task_count": task_count,
            })

        # 🔹 TOP STATS
        total_members = members.count()

        active_projects = ProjectMember.objects.filter(
            is_deleted=False
        ).values("project").distinct().count()

        tasks_in_progress = Task.objects.filter(
            status="in_progress",
            is_deleted=False
        ).count()

        last_7_days = now() - timedelta(days=7)
        completed_last_7 = Task.objects.filter(
            status="done",
            updated_at__gte=last_7_days,
            is_deleted=False
        ).count()

        return Response({
            "stats": {
                "total_members": total_members,
                "active_projects": active_projects,
                "tasks_in_progress": tasks_in_progress,
                "completed_last_7_days": completed_last_7,
            },
            "members": rows
        })



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
        
    @action(detail=True, methods=["get"], url_path="backlog")
    def backlog(self, request, pk=None):
        project = self.get_object()

        tasks = Task.objects.filter(
            project=project,
            # sprint__isnull=True,
            is_deleted=False
        ).exclude(status="done")

        return Response(TaskSerializer(tasks, many=True).data)



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
    
    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        sprint = self.get_object()

        # 🔐 Access control
        if request.user.role not in ["super_user", "admin"]:
            is_member = sprint.project.project_members.filter(
                user=request.user,
                is_deleted=False
            ).exists()

            if not is_member:
                return Response(
                    {"detail": "You do not have access to this sprint."},
                    status=403
                )

        logs = AuditLog.objects.filter(
            model_name__in=["Sprint", "Task"],
            object_id__in=[
                str(sprint.id)
            ] + list(
                sprint.tasks.values_list("id", flat=True)
            )
        ).select_related(
            "user"
        ).order_by("-created_at")

        serializer = SprintHistorySerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        sprint = self.get_object()

        tasks = sprint.tasks.filter(is_deleted=False)

        total_points = tasks.aggregate(
            total=models.Sum("estimated_hours")
        )["total"] or 0

        completed_points = tasks.filter(
            status="done"
        ).aggregate(
            total=models.Sum("estimated_hours")
        )["total"] or 0

        days_left = (sprint.end_date - now().date()).days if sprint.end_date else None

        progress = int((completed_points / total_points) * 100) if total_points else 0

        return Response({
            "sprint_name": sprint.name,
            "sprint_code": sprint.code,
            "status": sprint.status,
            "start_date": sprint.start_date,
            "end_date": sprint.end_date,
            "days_left": days_left,
            "story_points_target": sprint.story_points_target,
            "story_points_completed": completed_points,
            "progress_percent": progress,
            "health": "healthy" if progress >= 50 else "at_risk"
        })

    @action(detail=True, methods=["get"], url_path="board")
    def board(self, request, pk=None):
        sprint = self.get_object()

        tasks = sprint.tasks.filter(is_deleted=False)

        def serialize(qs):
            return TaskSerializer(qs, many=True).data

        return Response({
            "todo": serialize(tasks.filter(status="todo")),
            "in_progress": serialize(tasks.filter(status="in_progress")),
            "review": serialize(tasks.filter(status="review")),
            "done": serialize(tasks.filter(status="done")),
        })
    
    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        sprint = self.get_object()

        tasks = sprint.tasks.filter(is_deleted=False).order_by("position")

        return Response({
            "count": tasks.count(),
            "items": TaskSerializer(tasks, many=True).data
        })

    @action(detail=True, methods=["post"], url_path="add-task")
    def add_task(self, request, pk=None):
        sprint = self.get_object()
        task_id = request.data.get("task_id")

        task = get_object_or_404(
            Task,
            id=task_id,
            project=sprint.project,
            is_deleted=False
        )

        task.sprint = sprint
        task.position = sprint.tasks.count()
        task.updated_by = request.user
        task.save()

        return Response({"detail": "Task added to sprint"})

    @action(detail=True, methods=["get"], url_path="capacity")
    def capacity(self, request, pk=None):
        sprint = self.get_object()

        data = []
        members = sprint.project.project_members.select_related("user")

        for member in members:
            tasks = sprint.tasks.filter(assigned_to=member.user)

            used = tasks.aggregate(
                total=models.Sum("estimated_hours")
            )["total"] or 0

            capacity = sprint.default_capacity_hours or 40
            percent = int((used / capacity) * 100) if capacity else 0

            if percent >= 100:
                data.append({
                    "user": member.user.name,
                    "used": used,
                    "capacity": capacity,
                    "percent": percent,
                    "warning": True
                })

        return Response(data)

    @action(detail=True, methods=["get"], url_path="analytics")
    def analytics(self, request, pk=None):
        sprint = self.get_object()

        if request.user.role not in ["super_user", "admin"]:
            if not sprint.project.project_members.filter(
                user=request.user,
                is_deleted=False
            ).exists():
                return Response({"detail": "Forbidden"}, status=403)

        tasks = sprint.tasks.filter(is_deleted=False)
        total_points = tasks.aggregate(
            total=Sum("estimated_hours")
        )["total"] or 0

        # 📊 Burndown
        burndown = []
        sprint_days = (sprint.end_date - sprint.start_date).days + 1

        remaining = total_points
        completed_by_date = {}

        for task in tasks.filter(status="done", completed_at__isnull=False):
            day = task.completed_at.date()
            completed_by_date.setdefault(day, 0)
            completed_by_date[day] += task.estimated_hours or 0

        for i in range(sprint_days):
            day = sprint.start_date + timedelta(days=i)
            remaining -= completed_by_date.get(day, 0)

            ideal_remaining = max(
                total_points - (total_points / sprint_days) * i,
                0
            )

            burndown.append({
                "day": day.isoformat(),
                "ideal": round(ideal_remaining, 2),
                "actual": max(remaining, 0)
            })
        
        completed_sprints = Sprint.objects.filter(
            project=sprint.project,
            status="completed"
        ).order_by("-end_date")[:5]

        velocities = []

        for s in completed_sprints:
            points = s.tasks.filter(
                status="done"
            ).aggregate(
                total=Sum("estimated_hours")
            )["total"] or 0
            velocities.append(points)

        velocity = round(sum(velocities) / len(velocities), 1) if velocities else 0

        completed_points = tasks.filter(
            status="done"
        ).aggregate(
            total=Sum("estimated_hours")
        )["total"] or 0

        completion_percent = int(
            (completed_points / total_points) * 100
        ) if total_points else 0

        carry_over = tasks.exclude(status="done").count()

        actual_hours = tasks.aggregate(
            total=Sum("estimated_hours")
        )["total"] or 0

        if completion_percent >= 80:
            health = "healthy"
        elif completion_percent >= 50:
            health = "at_risk"
        else:
            health = "critical"

        return Response({
            "burndown": burndown,
            "velocity": velocity,
            "metrics": {
                "completion_percent": completion_percent,
                "carry_over_tasks": carry_over,
                "estimated_vs_actual": total_points - completed_points,
            },
            "health": health
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

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        milestone = self.get_object()

        # 🔐 Access control
        if request.user.role not in ["super_user", "admin"]:
            is_member = milestone.project.project_members.filter(
                user=request.user,
                is_deleted=False
            ).exists()

            if not is_member:
                return Response(
                    {"detail": "You do not have access to this milestone."},
                    status=403
                )

        # 🔍 Collect related task IDs
        task_ids = milestone.tasks.values_list("id", flat=True)

        logs = AuditLog.objects.filter(
            model_name__in=["Milestone", "Task"],
            object_id__in=[str(milestone.id)] + list(task_ids)
        ).select_related(
            "user"
        ).order_by("-created_at")

        serializer = MilestoneHistorySerializer(logs, many=True)
        return Response(serializer.data)
    

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
        user = self.request.user

        qs = TaskComment.objects.select_related(
            "task",
            "commented_by"
        )

        # 🔐 Admins see everything
        if user.role in ["super_user", "admin"]:
            return qs

        return qs.filter(
            Q(task__project__project_members__user=user) |
            Q(commented_by=user)
        ).distinct()



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
