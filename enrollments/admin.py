from django.contrib import admin
from .models import Enrollment, LessonProgress, Answer

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display   = ("student", "course", "enrolled_at")
    list_filter    = ("course",)
    search_fields  = ("student__username", "course__title")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display   = ("enrollment", "lesson", "completed")
    list_filter    = ("completed",)
    search_fields  = ("enrollment__student__username", "lesson__title")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display   = ("student", "question", "selected", "is_correct")
    list_filter    = ("is_correct",)
    search_fields  = ("student__username", "question__text")
