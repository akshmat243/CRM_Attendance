from django.core.management.base import BaseCommand
from django.utils.timezone import now

from project_ms.models import Milestone

class Command(BaseCommand):
    help = "Auto-close milestones whose due date has passed"

    def handle(self, *args, **kwargs):
        today = now().date()

        milestones = Milestone.objects.filter(
            status__in=["not_started", "in_progress", "blocked"],
            due_date__lt=today,
            is_deleted=False
        )

        updated = milestones.update(status="completed")

        self.stdout.write(
            self.style.SUCCESS(
                f"{updated} milestone(s) auto-closed."
            )
        )
        for milestone in milestones:
            milestone.project.activities.create(
                action="milestone_completed",
                description=f"Milestone '{milestone.name}' was auto-closed as its due date has passed."
            )