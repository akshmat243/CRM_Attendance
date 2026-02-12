from django.contrib import admin
from .models import (
    Project,
    ProjectMember,
    Task,
    TaskComment,
    TaskActivity,
    Sprint,
    Milestone,
    MilestoneCriteria,
)



class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = ("is_deleted",)
    actions = ["restore_selected"]

    def restore_selected(self, request, queryset):
        for obj in queryset:
            obj.restore()
        self.message_user(request, "Selected items restored.")


class MilestoneCriteriaInline(admin.TabularInline):
    model = MilestoneCriteria
    extra = 1
    fields = ("title", "is_completed")
    readonly_fields = ()

class MilestoneTaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = (
        "title",
        "assigned_to",
        "status",
        "priority",
        "due_date",
        "completed_at",
    )
    readonly_fields = fields
    can_delete = False
    show_change_link = True

class SprintTaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = (
        "title",
        "assigned_to",
        "status",
        "priority",
        "position",
        "completed_at",
    )
    readonly_fields = fields
    can_delete = False
    show_change_link = True



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        # "code",
        "start_date",
        "end_date",
        "created_by",
        "created_at",
    )

    search_fields = ("name",)
    list_filter = ("status",)
    readonly_fields = ("created_by", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# @admin.register(ProjectMember)
# class ProjectMemberAdmin(admin.ModelAdmin):
#     list_display = (
#         "project",
#         "user",
#         "role",
#         "assigned_by",
#         "assigned_at",
#     )

#     list_filter = (
#         "role",
#         "assigned_at",
#     )

#     search_fields = (
#         "project__name",
#         "user__username",
#         "user__email",
#     )

#     readonly_fields = (
#         "id",
#         "assigned_at",
#     )
    
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "assigned_to",
        "status",
        "priority",
        "sprint",
        "milestone",
        "due_date",
        "created_by",
        "updated_by",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "project",
        "sprint",
        "milestone",
    )

    search_fields = (
        "title",
        "description",
        "assigned_to__name",
        "created_by__name",
    )

    readonly_fields = (
        "id",
        "slug",
        "assigned_at",
        "completed_at",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    autocomplete_fields = (
        "project",
        "assigned_to",
        "sprint",
        "milestone",
    )

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "title",
                "slug",
                "description",
                "project",
            )
        }),
        ("Assignment", {
            "fields": (
                "assigned_to",
                "assigned_at",
            )
        }),
        ("Agile Planning", {
            "fields": (
                "sprint",
                "milestone",
                "priority",
                "status",
                "position",
                "estimated_hours",
            )
        }),
        ("Dates", {
            "fields": (
                "due_date",
                "completed_at",
            )
        }),
        ("Audit", {
            "fields": (
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "project",
        "status",
        "start_date",
        "end_date",
    )

    list_filter = ("status", "project")
    autocomplete_fields = ("project",)
    search_fields = ("name",)
    inlines = (SprintTaskInline,)


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "status",
        "priority",
        "due_date",
        "owner",
    )

    list_filter = (
        "status",
        "priority",
        "project",
    )

    search_fields = ("title",)

    autocomplete_fields = ("project", "owner")

    inlines = (
        MilestoneCriteriaInline,
        MilestoneTaskInline,
    )

    readonly_fields = (
        "created_by",
        "created_at",
        "updated_at",
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "user",
        "role",
        "assigned_by",
        "assigned_at",
    )

    list_filter = ("role", "project")
    search_fields = ("user__name", "project__name")
    autocomplete_fields = ("project", "user", "assigned_by")

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
