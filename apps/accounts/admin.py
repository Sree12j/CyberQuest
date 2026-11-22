from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CyberQuestUserAdmin(UserAdmin):
    """Standard Django user admin with CyberQuest profile fields added."""

    fieldsets = UserAdmin.fieldsets + (
        (
            "CyberQuest profile",
            {"fields": ("display_name", "created_at", "updated_at")},
        ),
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("username", "display_name", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "display_name")
    ordering = ("username",)
