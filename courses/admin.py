# courses/admin.py
import nested_admin
from django.contrib import admin

from .models import (
    Category,
    Course,
    Lesson,
    FollowUpQuestion,
    FollowUpOption,
    Quiz,
    QuizQuestion,
    QuizOption,
    ExamProject,
    Order,
)
#
# ─── Category/Admin ───────────────────────────────────────────────────────────────
#
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("name",)
    search_fields = ("name",)


#
# ─── Course/Admin ─────────────────────────────────────────────────────────────────
#
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display   = (
        "title",
        "category",
        "instructor",
        "price",
        "is_free",
        "created_at"
    )
    list_filter    = ("category", "instructor", "is_free")
    search_fields  = ("title", "description", "instructor__username")


#
# ─── FollowUpOption Inline ─────────────────────────────────────────────────────────
#
class FollowUpOptionInline(nested_admin.NestedTabularInline):
    model = FollowUpOption
    extra = 4
    fields = ("label", "text", "is_correct")


#
# ─── FollowUpQuestion Inline (nested to include its Options) ───────────────────────
#
class FollowUpQuestionInline(nested_admin.NestedStackedInline):
    model = FollowUpQuestion
    extra = 1
    fields = ("question_text", "solution_text", "allow_multiple")
    inlines = [FollowUpOptionInline]


#
# ─── Lesson/Admin (Nested: includes FollowUpQuestionInline) ───────────────────────
#
@admin.register(Lesson)
class LessonAdmin(nested_admin.NestedModelAdmin):
    list_display   = ("title", "course", "order", "is_free", "created_at")
    list_filter    = ("course", "is_free")
    search_fields  = ("title", "content")
    inlines        = [FollowUpQuestionInline]


#
# ─── QuizOption Inline ─────────────────────────────────────────────────────────────
#
class QuizOptionInline(nested_admin.NestedTabularInline):
    model = QuizOption
    extra = 4
    fields = ("label", "text", "is_correct")


#
# ─── QuizQuestion Inline (nested to include its Options) ──────────────────────────
#
class QuizQuestionInline(nested_admin.NestedStackedInline):
    model = QuizQuestion
    extra = 1
    fields = ("question_text", "solution_text", "allow_multiple")
    inlines = [QuizOptionInline]


#
# ─── Quiz/Admin (Nested: includes QuizQuestionInline) ──────────────────────────────
#
@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    list_display   = ("course", "title", "created_at")
    list_filter    = ("course", "title")
    search_fields  = ("course__title",)
    inlines        = [QuizQuestionInline]


#
# ─── ExamProject/Admin ─────────────────────────────────────────────────────────────
#
@admin.register(ExamProject)
class ExamProjectAdmin(admin.ModelAdmin):
    list_display    = ("course", "student", "submitted_at", "score", "is_approved")
    list_filter     = ("course", "is_approved")
    search_fields   = ("student__username",)
    readonly_fields = ("submitted_at",)


#
# ─── Order/Admin ──────────────────────────────────────────────────────────────────
#
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ("id", "student", "course", "amount", "status", "created_at")
    list_filter     = ("status", "course")
    search_fields   = ("student__username", "transaction_id")
    readonly_fields = ("created_at", "updated_at")
