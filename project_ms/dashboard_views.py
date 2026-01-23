from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Project, Task
from .serializers import DashboardStatsSerializer

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
