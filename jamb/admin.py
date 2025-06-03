# jamb/admin.py

from django.contrib import admin
from .models import JAMBSubject, JAMBQuestion, Strategy

@admin.register(JAMBSubject)
class JAMBSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "topics",
        "duration",
    )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    list_filter = ("topics",)


@admin.register(JAMBQuestion)
class JAMBQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "short_question",
        "correct_choice",
    )
    list_filter = ("subject", "correct_choice")
    search_fields = ("question_text",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject",
                    "question_text",
                )
            },
        ),
        (
            "Options",
            {
                "fields": (
                    ("option_a", "option_b"),
                    ("option_c", "option_d"),
                )
            },
        ),
        (
            "Answer Key",
            {
                "fields": ("correct_choice",),
                "description": "Mark which option (A–D) is correct.",
            },
        ),
    )

    def short_question(self, obj):
        text = obj.question_text
        return (text[:75] + "...") if len(text) > 75 else text

    short_question.short_description = "Question (truncated)"


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ("category",)
    search_fields = ("category",)
    ordering = ("category",)
