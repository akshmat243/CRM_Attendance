from django.apps import AppConfig
import sys

class ProjectMsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_ms'
    
    def ready(self):
        # 🔴 DO NOT register signals during migrate
        if "migrate" in sys.argv or "makemigrations" in sys.argv:
            return

        import project_ms.signals
