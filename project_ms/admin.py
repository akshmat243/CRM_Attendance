from django.contrib import admin
from .models import (
    Project,
    ProjectMember,
    Task,
    TaskComment,
    TaskActivity
)



class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = ("is_deleted",)
    actions = ["restore_selected"]

    def restore_selected(self, request, queryset):
        for obj in queryset:
            obj.restore()
        self.message_user(request, "Selected items restored.")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "is_active",
        "created_by",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "slug",
    )

    readonly_fields = (
        "id",
        "slug",
        "created_at",
        "updated_at",
    )

    # prepopulated_fields = {"slug": ("name",)}

    ordering = ("-created_at",)

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "user",
        "role",
        "assigned_by",
        "assigned_at",
    )

    list_filter = (
        "role",
        "assigned_at",
    )

    search_fields = (
        "project__name",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "id",
        "assigned_at",
    )

@admin.register(Task)
class TaskAdmin(SoftDeleteAdmin):
    list_display = (
        "title",
        "project",
        "assigned_to",
        "priority",
        "status",
        "due_date",
        "is_active",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "is_active",
        "project",
    )

    search_fields = (
        "title",
        "description",
        "slug",
        "project__name",
        "assigned_to__username",
        "assigned_to__email",
    )

    readonly_fields = (
        "id",
        "slug",
        "created_at",
        "updated_at",
    )

    # prepopulated_fields = {"slug": ("title",)}

    ordering = ("-created_at",)

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "commented_by",
        "created_at",
    )

    search_fields = (
        "task__title",
        "comment",
        "commented_by__username",
        "commented_by__email",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)

@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "action",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "task__title",
        "performed_by__username",
        "performed_by__email",
        "description",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)
