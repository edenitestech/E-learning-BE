# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("E-Learning Flags", {"fields": ("is_instructor",)}),
    )
    list_display = ("username", "email", "is_staff", "is_instructor", "is_active")
    list_filter  = ("is_staff", "is_instructor", "is_active")
    search_fields = ("username", "email")
