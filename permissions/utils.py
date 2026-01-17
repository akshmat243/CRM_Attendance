from .models import RoleModelPermission, AppModel, PermissionType


def has_model_permission(user, model, action):
    """
    action = view | add | change | delete
    """
    if user.role == "super_user":
        return True

    app_model = AppModel.objects.filter(
        app_label=model._meta.app_label,
        model_name=model.__name__
    ).first()

    permission = PermissionType.objects.filter(code=action).first()

    if not app_model or not permission:
        return False

    return RoleModelPermission.objects.filter(
        role=user.role,
        app_model=app_model,
        permission=permission
    ).exists()


def create_crud_permissions(app_model):
    PERMISSIONS = [
        ("view", "View"),
        ("add", "Add"),
        ("change", "Change"),
        ("delete", "Delete"),
    ]

    for code, label in PERMISSIONS:
        PermissionType.objects.get_or_create(
            code=code,
            defaults={"name": label}
        )
