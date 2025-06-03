from django.contrib import admin
from .models import Lesson, Question, Option

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display  = ("title", "course", "is_free", "created_at")
    list_filter   = ("course", "is_free")
    search_fields = ("title", "course__title")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ("id", "lesson", "text", "allow_multiple", "created_at")
    list_filter   = ("lesson", "allow_multiple")
    search_fields = ("text", "lesson__title")


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display  = ("question", "label", "text", "is_correct")
    list_filter   = ("is_correct", "label")
    search_fields = ("text", "question__text")
