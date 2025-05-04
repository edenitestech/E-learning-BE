from django.contrib import admin
from .models import Lesson, Question

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display   = ("title", "course", "is_free", "created_at")
    list_filter    = ("course", "is_free")
    search_fields  = ("title", "course__title")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display   = ("id", "lesson", "text", "correct_choice")
    list_filter    = ("lesson",)
    search_fields  = ("text", "lesson__title")
