from django.contrib import admin
from .models import AppModel, PermissionType, RoleModelPermission


admin.site.register(AppModel)
admin.site.register(PermissionType)
admin.site.register(RoleModelPermission)
