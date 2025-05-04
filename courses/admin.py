from django.contrib import admin
from .models import Category, Course, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("name",)
    search_fields = ("name",)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display   = ("title", "category", "instructor", "price", "created_at")
    list_filter    = ("category", "instructor")
    search_fields  = ("title", "description", "instructor__username")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ("id", "student", "course", "amount", "status", "created_at")
    list_filter     = ("status", "course")
    search_fields   = ("student__username", "transaction_id")
    readonly_fields = ("created_at", "updated_at")
