# exams/admin.py
from django.contrib import admin
from .models import ExamSubject, PastQuestion, PastOption
# ─── ExamSubject Admin ─────────────────────────────────────────────────────────────
#
@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display   = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields  = ("name",)


#
# ─── PastOptionInline (shows A–D choices under each question) ─────────────────────
#
class PastOptionInline(admin.TabularInline):
    model = PastOption
    extra = 4
    fields = ("label", "text", "is_correct")


#
# ─── PastQuestion Admin ────────────────────────────────────────────────────────────
#
@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display   = ("exam_type", "year", "subject", "short_question")
    list_filter    = ("exam_type", "year", "subject__name")
    search_fields  = ("question_text", "subject__name")
    inlines        = [PastOptionInline]
    readonly_fields = ("created_at",)

    def short_question(self, obj):
        return obj.question_text[:50]
    short_question.short_description = "Question (truncated)"


#
# ─── PastOption Admin (separate page if you want to ever see options individually) ─
#
@admin.register(PastOption)
class PastOptionAdmin(admin.ModelAdmin):
    list_display   = ("question", "label", "text", "is_correct")
    list_filter    = ("question__exam_type", "question__year", "question__subject__name")
    search_fields  = ("text", "question__question_text")

