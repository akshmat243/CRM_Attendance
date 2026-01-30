from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import calculate_percentage, percentage
from datetime import timedelta
from .models import Project, Task, ProjectMember
from django.db.models import Q, Count
from rest_framework.exceptions import PermissionDenied
from datetime import date
from django.db.models import F, ExpressionWrapper, IntegerField
from django.db.models.functions import Cast
from .serializers import DashboardStatsSerializer, ActiveTaskListSerializer, UpcomingDeadlineSerializer, TeamWorkloadSerializer

class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()

        # 🔐 Project Scope
        if user.role in ["super_user", "admin"]:
            projects = Project.objects.all()
            tasks = Task.objects.all()
        else:
            projects = Project.objects.prefetch_related(
                "tasks"
            )

            tasks = Task.objects.select_related(
                "project", "assigned_to"
            )


        data = {
            "total_projects": projects.count(),
            "active_projects": projects.filter(status="in_progress").count(),
            "completed_projects": projects.filter(status="completed").count(),

            "total_tasks": tasks.count(),
            "todo_tasks": tasks.filter(status="todo").count(),
            "in_progress_tasks": tasks.filter(status="in_progress").count(),
            "review_tasks": tasks.filter(status="review").count(),
            "done_tasks": tasks.filter(status="done").count(),

            "overdue_tasks": tasks.filter(
                due_date__lt=today,
                status__in=["todo", "in_progress", "review"]
            ).count(),
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)

class MyTaskStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()

        tasks = Task.objects.filter(assigned_to=user)

        data = {
            "total_tasks": tasks.count(),
            "todo_tasks": tasks.filter(status="todo").count(),
            "in_progress_tasks": tasks.filter(status="in_progress").count(),
            "review_tasks": tasks.filter(status="review").count(),
            "done_tasks": tasks.filter(status="done").count(),
            "overdue_tasks": tasks.filter(
                due_date__lt=today,
                status__in=["todo", "in_progress", "review"]
            ).count(),
        }

        return Response(data)

class ProjectTaskStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user = request.user

        if user.role not in ["super_user", "admin"]:
            if not Project.objects.filter(
                id=project_id,
                project_members__user=user
            ).exists():
                return Response(
                    {"detail": "Not allowed"},
                    status=403
                )

        tasks = Task.objects.filter(project_id=project_id)

        return Response({
            "todo": tasks.filter(status="todo").count(),
            "in_progress": tasks.filter(status="in_progress").count(),
            "review": tasks.filter(status="review").count(),
            "done": tasks.filter(status="done").count(),
        })


class DashboardCardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()

        # Date ranges
        start_this_month = today.replace(day=1)
        start_last_month = (start_this_month - timedelta(days=1)).replace(day=1)
        end_last_month = start_this_month - timedelta(days=1)

        if user.role in ["super_user", "admin"]:
            project_qs = Project.objects.filter(is_deleted=False)
            task_qs = Task.objects.filter(is_deleted=False)
            member_qs = ProjectMember.objects.filter(is_deleted=False)
        else:
            project_qs = Project.objects.filter(
                project_members__user=user,
                is_deleted=False
            ).distinct()

            task_qs = Task.objects.filter(
                Q(assigned_to=user) |
                Q(project__project_members__user=user),
                is_deleted=False
            ).distinct()

            member_qs = ProjectMember.objects.filter(
                project__project_members__user=user,
                is_deleted=False
            ).distinct()

        total_projects_now = project_qs.filter(
            created_at__date__gte=start_this_month
        ).count()

        total_projects_prev = project_qs.filter(
            created_at__date__range=[start_last_month, end_last_month]
        ).count()

        active_tasks_now = task_qs.filter(
            status__in=["todo", "in_progress", "review"],
            created_at__date__gte=start_this_month
        ).count()

        active_tasks_prev = task_qs.filter(
            status__in=["todo", "in_progress", "review"],
            created_at__date__range=[start_last_month, end_last_month]
        ).count()

        completed_tasks_now = task_qs.filter(
            status="done",
            updated_at__date__gte=start_this_month
        ).count()

        completed_tasks_prev = task_qs.filter(
            status="done",
            updated_at__date__range=[start_last_month, end_last_month]
        ).count()

        team_members_now = member_qs.filter(
            assigned_at__date__gte=start_this_month
        ).count()

        team_members_prev = member_qs.filter(
            assigned_at__date__range=[start_last_month, end_last_month]
        ).count()

        data = {
            "total_projects": {
                "count": project_qs.count(),
                "change_percent": calculate_percentage(
                    total_projects_now,
                    total_projects_prev
                )
            },
            "active_tasks": {
                "count": task_qs.filter(
                    status__in=["todo", "in_progress", "review"]
                ).count(),
                "change_percent": calculate_percentage(
                    active_tasks_now,
                    active_tasks_prev
                )
            },
            "completed_tasks": {
                "count": task_qs.filter(status="done").count(),
                "change_percent": calculate_percentage(
                    completed_tasks_now,
                    completed_tasks_prev
                )
            },
            "team_members": {
                "count": member_qs.count(),
                "change_percent": calculate_percentage(
                    team_members_now,
                    team_members_prev
                )
            }
        }

        return Response(data)


class ActiveTasksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        ACTIVE_STATUSES = ["todo", "in_progress", "review"]

        qs = Task.objects.select_related(
            "project",
            "assigned_to"
        ).filter(
            status__in=ACTIVE_STATUSES,
            is_deleted=False
        )

        # Super user & admin → all active tasks
        if user.role in ["super_user", "admin"]:
            tasks = qs.order_by("-updated_at")[:5]

        # Team leader → tasks in their projects
        elif user.role == "team_leader":
            tasks = qs.filter(
                project__project_members__user=user,
                project__project_members__is_deleted=False
            ).distinct().order_by("-updated_at")[:5]

        # Staff / freelancer / IT staff → only their tasks
        else:
            tasks = qs.filter(
                assigned_to=user
            ).order_by("-updated_at")[:5]

        serializer = ActiveTaskListSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskStatusOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        qs = Task.objects.filter(
            is_deleted=False
        )

        # Visibility rules
        if user.role in ["super_user", "admin"]:
            tasks = qs

        elif user.role == "team_leader":
            tasks = qs.filter(
                project__project_members__user=user,
                project__project_members__is_deleted=False
            ).distinct()

        else:
            tasks = qs.filter(
                assigned_to=user
            )

        total = tasks.count()

        todo_count = tasks.filter(status="todo").count()
        in_progress_count = tasks.filter(status="in_progress").count()
        done_count = tasks.filter(status="done").count()

        data = {
            "total_tasks": total,
            "todo": {
                "count": todo_count,
                "percentage": percentage(todo_count, total)
            },
            "in_progress": {
                "count": in_progress_count,
                "percentage": percentage(in_progress_count, total)
            },
            "done": {
                "count": done_count,
                "percentage": percentage(done_count, total)
            }
        }

        return Response(data)

class UpcomingDeadlinesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        qs = Task.objects.select_related(
            "project"
        ).filter(
            due_date__gte=today,
            status__in=["todo", "in_progress", "review"],
            is_deleted=False
        )

        # Visibility rules
        if user.role in ["super_user", "admin"]:
            tasks = qs

        elif user.role == "team_leader":
            tasks = qs.filter(
                project__project_members__user=user,
                project__project_members__is_deleted=False
            ).distinct()

        else:
            tasks = qs.filter(
                assigned_to=user
            )

        # Annotate days left
        tasks = tasks.annotate(
            days_left=ExpressionWrapper(
                Cast(F("due_date"), output_field=IntegerField()) -
                Cast(today, output_field=IntegerField()),
                output_field=IntegerField()
            )
        ).order_by("due_date")[:5]

        serializer = UpcomingDeadlineSerializer(tasks, many=True)
        return Response(serializer.data)


class TeamWorkloadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 🔐 Only leaders & admins can view workload
        if user.role not in ["super_user", "admin", "team_leader"]:
            raise PermissionDenied("You are not allowed to view team workload.")

        ACTIVE_STATUSES = ["todo", "in_progress", "review"]

        # -----------------------------
        # Determine team members
        # -----------------------------
        if user.role in ["super_user", "admin"]:
            members = ProjectMember.objects.filter(
                is_deleted=False
            ).select_related("user")

        else:  # team_leader
            members = ProjectMember.objects.filter(
                project__project_members__user=user,
                is_deleted=False
            ).select_related("user").distinct()

        users = [m.user for m in members]

        # -----------------------------
        # Task counts per user
        # -----------------------------
        task_counts = (
            Task.objects.filter(
                assigned_to__in=users,
                status__in=ACTIVE_STATUSES,
                is_deleted=False
            )
            .values("assigned_to")
            .annotate(task_count=Count("id"))
        )

        task_count_map = {
            item["assigned_to"]: item["task_count"]
            for item in task_counts
        }

        max_tasks = max(task_count_map.values(), default=1)

        # -----------------------------
        # Build response
        # -----------------------------
        data = []
        for member in members:
            count = task_count_map.get(member.user.id, 0)

            data.append({
                "user_id": member.user.id,
                "name": member.user.name or member.user.username,
                "role": "Team Member",
                "task_count": count,
                "workload_percent": round((count / max_tasks) * 100),
            })

        return Response(data)
