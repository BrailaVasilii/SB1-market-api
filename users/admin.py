from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
    ]

    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]

    readonly_fields = []

    ordering = ["-id"]

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("email", "first_name", "last_name", "phone", "city")},
        ),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
    )
