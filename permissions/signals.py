# from django.apps import apps
# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
# from .models import AppModel


# @receiver(post_migrate)
# def register_models(sender, **kwargs):
#     for model in apps.get_models():
#         AppModel.objects.get_or_create(
#             app_label=model._meta.app_label,
#             model_name=model.__name__
#         )



from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .utils import create_crud_permissions
from .models import AppModel

TARGET_APP_LABEL = "project_ms"   # 👈 jis app ke models chahiye


@receiver(post_migrate)
def register_models_and_permissions(sender, **kwargs):
    # Run ONLY for target app
    if sender.label != TARGET_APP_LABEL:
        return

    app_config = apps.get_app_config(TARGET_APP_LABEL)

    for model in app_config.get_models():
        # 1️⃣ Register model
        app_model, _ = AppModel.objects.get_or_create(
            app_label=TARGET_APP_LABEL,
            model_name=model.__name__,
        )

        # 2️⃣ Create only 4 permissions
        create_crud_permissions(app_model)

