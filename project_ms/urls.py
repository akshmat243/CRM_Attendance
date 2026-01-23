from rest_framework import routers
from django.urls import path, include
from .views import (
    ProjectViewSet,
    ProjectMemberViewSet,
    ProjectActivityViewSet,
    TaskViewSet,
    TaskCommentViewSet,
    TaskActivityViewSet,
    NotificationViewSet,
)
router = routers.DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("project-members", ProjectMemberViewSet, basename="project-member")
router.register("tasks", TaskViewSet, basename="task")
router.register("task-comments", TaskCommentViewSet, basename="task-comment")
router.register("task-activities", TaskActivityViewSet, basename="task-activity")
router.register("project-activities", ProjectActivityViewSet, basename="project-activity")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls))
]

from .dashboard_views import (
    DashboardStatsAPIView,
    MyTaskStatsAPIView,
    ProjectTaskStatsAPIView,
)

urlpatterns += [
    path("dashboard/stats/", DashboardStatsAPIView.as_view()),
    path("dashboard/my-tasks/", MyTaskStatsAPIView.as_view()),
    path(
        "dashboard/project/<uuid:project_id>/tasks/",
        ProjectTaskStatsAPIView.as_view()
    ),
]
