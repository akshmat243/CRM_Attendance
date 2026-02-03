from django.core.management.base import BaseCommand
from django.utils.timezone import now

from project_ms.models import Sprint

class Command(BaseCommand):
    help = "Auto-close sprints whose end date has passed"

    def handle(self, *args, **kwargs):
        today = now().date()

        sprints = Sprint.objects.filter(
            auto_close=True,
            status__in=["planned", "active"],
            end_date__lt=today,
            is_deleted=False
        )

        updated = sprints.update(status="completed")

        self.stdout.write(
            self.style.SUCCESS(
                f"{updated} sprint(s) auto-closed."
            )
        )
        for sprint in sprints:
            sprint.project.activities.create(
                action="sprint_completed",
                description=f"Sprint '{sprint.name}' was auto-closed as its end date has passed."
            )