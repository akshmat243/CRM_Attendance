from django.apps import AppConfig


class ProjectMsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project_ms'
    
    def ready(self):
        import project_ms.signals
