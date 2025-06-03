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
    FollowUpQuestion,
    FollowUpOption,
)


#
# Category/Admin
#
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ("name",)
    search_fields = ("name",)


#
# Course/Admin
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
# Lesson & FollowUpQuestion/Admin
#
class FollowUpOptionInline(admin.TabularInline):
    model = FollowUpOption
    extra = 4


class FollowUpQuestionInline(admin.StackedInline):
    model = FollowUpQuestion
    extra = 1
    inlines = [FollowUpOptionInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display  = ("title", "course", "order", "is_free", "created_at")
    list_filter   = ("course", "is_free")
    search_fields = ("title", "content")
    inlines       = [FollowUpQuestionInline]


#
# Quiz & QuizQuestion/Admin
#
class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4


class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 1
    inlines = [QuizOptionInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display  = ("course", "title", "created_at")
    list_filter   = ("course", "title")
    search_fields = ("course__title",)
    inlines       = [QuizQuestionInline]


#
# ExamProject/Admin
#
@admin.register(ExamProject)
class ExamProjectAdmin(admin.ModelAdmin):
    list_display    = ("course", "student", "submitted_at", "score", "is_approved")
    list_filter     = ("course", "is_approved")
    search_fields   = ("student__username",)
    readonly_fields = ("submitted_at",)


#
# Order/Admin
#
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ("id", "student", "course", "amount", "status", "created_at")
    list_filter     = ("status", "course")
    search_fields   = ("student__username", "transaction_id")
    readonly_fields = ("created_at", "updated_at")

# --------------------------------------------------------------------
#  Inline the Options under a “Question” admin
# --------------------------------------------------------------------
class FollowUpOptionInline(admin.TabularInline):
    model = FollowUpOption
    extra = 4
    fields = ("label", "text", "is_correct")

@admin.register(FollowUpQuestion)
class FollowUpQuestionAdmin(admin.ModelAdmin):
    list_display   = ("short_text", "lesson")
    list_filter    = ("lesson__course",)
    search_fields  = ("question_text",)
    inlines        = [FollowUpOptionInline]

    def short_text(self, obj):
        return obj.question_text[:50]
    short_text.short_description = "Question (truncated)"


# --------------------------------------------------------------------
#  Still inline “Question” under a “Lesson” admin, but without nesting “Options”
# --------------------------------------------------------------------
class FollowUpQuestionInline(admin.StackedInline):
    model = FollowUpQuestion
    extra = 1
    fields = ("question_text", "allow_multiple")
    # No nested “inlines” attribute here.


