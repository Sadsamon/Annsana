from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Annsana profile",
            {
                "fields": (
                    "display_name",
                    "bio",
                    "avatar",
                    "location",
                    "cultural_affiliation",
                    "is_contributor",
                )
            },
        ),
    )
    list_display = ("username", "email", "display_name", "is_contributor", "is_staff")
    list_filter = DjangoUserAdmin.list_filter + ("is_contributor",)
    search_fields = ("username", "email", "display_name")
