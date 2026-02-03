from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta

from project_ms.models import Milestone
from project_ms.notification import notify_project_members


class Command(BaseCommand):
    help = "Notify users about milestones due soon"

    def handle(self, *args, **kwargs):
        today = now().date()
        warning_date = today + timedelta(days=3)

        milestones = Milestone.objects.filter(
            due_date__range=[today, warning_date],
            status__in=["not_started", "in_progress", "blocked"],
            is_deleted=False
        )

        for milestone in milestones:
            notify_project_members(
                project=milestone.project,
                title="Milestone Due Soon",
                message=(
                    f"Milestone '{milestone.title}' "
                    f"is due on {milestone.due_date}."
                ),
                notification_type="project",
                extra_users=[milestone.owner] if milestone.owner else None
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{milestones.count()} milestone due notifications sent."
            )
        )
