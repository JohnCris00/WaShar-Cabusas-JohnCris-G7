from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class WaSharUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("WaShar", {"fields": ("role", "contact_number", "profile_photo", "vehicle_plate", "vehicle_model", "vehicle_type")}),
    )
