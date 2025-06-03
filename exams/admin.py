from django.contrib import admin
from .models import PastQuestion, Option, Subject

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4

@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam_type", "year", "subject", "question_text")
    list_filter = ("exam_type", "year", "subject")
    search_fields = ("question_text", "subject__name")
    inlines = [OptionInline]

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
