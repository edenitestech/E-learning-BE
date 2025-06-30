# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .models import Notification, Message

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("E-Learning Flags", {"fields": ("is_instructor",)}),
    )
    list_display = ("username", "email", "is_staff", "is_instructor", "is_active")
    list_filter  = ("is_staff", "is_instructor", "is_active")
    search_fields = ("username", "email")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "verb", "is_read", "created_at")
    list_filter  = ("is_read",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "subject", "is_read", "sent_at")
    list_filter  = ("is_read",)
    search_fields = ("subject", "body", "sender__username", "recipient__username")
