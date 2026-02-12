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
    SprintViewSet,
    SprintTaskListAPIView,
    NotificationUnreadCountAPIView,
    AuditLogViewSet,
    MilestoneViewSet,
    UserViewSet,
    TeamOverviewAPIView,
)
router = routers.DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("project-members", ProjectMemberViewSet, basename="project-member")
router.register("tasks", TaskViewSet, basename="task")
router.register("task-comments", TaskCommentViewSet, basename="task-comment")
router.register("task-activities", TaskActivityViewSet, basename="task-activity")
router.register("project-activities", ProjectActivityViewSet, basename="project-activity")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("sprints", SprintViewSet, basename="sprint")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")
router.register("milestones", MilestoneViewSet, basename="milestone")
router.register("users", UserViewSet, basename="user")


urlpatterns = [
    path("", include(router.urls)),
    path(
    "notifications/unread-count/",
    NotificationUnreadCountAPIView.as_view(),
    ),
    path("sprints/<uuid:sprint_id>/tasks/", SprintTaskListAPIView.as_view(),),
    path("team/overview/", TeamOverviewAPIView.as_view()),
    
]

from .dashboard_views import (
    DashboardStatsAPIView,
    MyTaskStatsAPIView,
    ProjectTaskStatsAPIView,
    DashboardCardAPIView,
    ActiveTasksAPIView,
    TaskStatusOverviewAPIView,
    UpcomingDeadlinesAPIView,
    TeamWorkloadAPIView,
    SprintBoardAPIView,
    SprintProgressAPIView,
    SprintBurndownAPIView,
    SprintCapacityVelocityAPIView,
    MilestoneDashboardAPIView,
)

urlpatterns += [
    path("dashboard/stats/", DashboardStatsAPIView.as_view()),
    path("dashboard/my-tasks/", MyTaskStatsAPIView.as_view()),
    path(
        "dashboard/project/<uuid:project_id>/tasks/",
        ProjectTaskStatsAPIView.as_view()
    ),
    path("dashboard/cards/", DashboardCardAPIView.as_view()),
    path("dashboard/active-tasks/", ActiveTasksAPIView.as_view()),
    path(
        "dashboard/task-status-overview/",
        TaskStatusOverviewAPIView.as_view()
    ),
    path(
        "dashboard/upcoming-deadlines/",
        UpcomingDeadlinesAPIView.as_view()
    ),
    path(
        "dashboard/team-workload/",
        TeamWorkloadAPIView.as_view()
    ),
    path(
        "sprints/<uuid:sprint_id>/board/",
        SprintBoardAPIView.as_view()
    ),
    path(
        "sprints/<uuid:sprint_id>/progress/",
        SprintProgressAPIView.as_view()
    ),
    path(
        "sprints/<uuid:sprint_id>/burndown/",
        SprintBurndownAPIView.as_view()
    ),
    path(
        "sprints/<uuid:sprint_id>/capacity-velocity/",
        SprintCapacityVelocityAPIView.as_view()
    ),
    path(
        "dashboard/milestones/",
        MilestoneDashboardAPIView.as_view()
    ),
]
