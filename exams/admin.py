from django.contrib import admin
from .models import PastQuestion

@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display   = ("exam_type", "year", "subject")
    list_filter    = ("exam_type", "year")
    search_fields  = ("subject",)
