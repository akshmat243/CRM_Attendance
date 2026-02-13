from django.contrib import admin
from .models import AppModel, PermissionType, RoleModelPermission


admin.site.register(AppModel)
admin.site.register(PermissionType)

@admin.register(RoleModelPermission)
class RoleModelPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "role",
        "app_model",
        "permission",
    )

    list_filter = (
        "role",
        "app_model__app_label",
        "permission",
    )

    search_fields = (
        "role",
        "app_model__model_name",
        "permission__code",
        "permission__name",
    )

    ordering = ("role", "app_model", "permission")

    # autocomplete_fields = ("app_model", "permission")

    # Optional: cleaner UI
    list_per_page = 25

