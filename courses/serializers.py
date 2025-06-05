import hmac
import hashlib
import requests

from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model

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
    Order
)

User = get_user_model()


#
# ─── CategorySerializer ────────────────────────────────────────────────────────────
#
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]


#
# ─── CourseSerializer ──────────────────────────────────────────────────────────────
#
class CourseSerializer(serializers.ModelSerializer):
    # Represent `category` by name on read; allow “category” (slug) on write
    category   = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Category.objects.all()
    )
    instructor = serializers.CharField(read_only=True, source="instructor.username")
    is_free    = serializers.BooleanField(default=False)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "category",
            "instructor",
            "price",
            "is_free",
            "created_at",
        ]
        read_only_fields = ["id", "instructor", "created_at"]


#
# ─── FollowUpOptionSerializer ───────────────────────────────────────────────────────
#
class FollowUpOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpOption
        fields = ["id", "label", "text", "is_correct"]
        read_only_fields = ["id"]


#
# ─── FollowUpQuestionSerializer ────────────────────────────────────────────────────
#
class FollowUpQuestionSerializer(serializers.ModelSerializer):
    options = FollowUpOptionSerializer(many=True)
    # newly exposed field:
    solution_text = serializers.CharField()

    class Meta:
        model = FollowUpQuestion
        fields = [
            "id",
            "question_text",
            "solution_text",
            "allow_multiple",
            "options"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        opts_data = validated_data.pop("options", [])
        question = FollowUpQuestion.objects.create(**validated_data)
        for opt in opts_data:
            FollowUpOption.objects.create(question=question, **opt)
        return question

    def update(self, instance, validated_data):
        opts_data = validated_data.pop("options", [])
        instance.question_text  = validated_data.get("question_text", instance.question_text)
        instance.solution_text  = validated_data.get("solution_text", instance.solution_text)
        instance.allow_multiple = validated_data.get("allow_multiple", instance.allow_multiple)
        instance.save()

        # Replace all options if provided
        if opts_data is not None:
            instance.options.all().delete()
            for opt_data in opts_data:
                FollowUpOption.objects.create(question=instance, **opt_data)
        return instance


#
# ─── LessonSerializer (nested FollowUpQuestions) ───────────────────────────────────
#
class LessonSerializer(serializers.ModelSerializer):
    followup_questions = FollowUpQuestionSerializer(many=True, required=False)
    video              = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "order",
            "title",
            "content",
            "video",
            "is_free",
            "followup_questions",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        questions_data = validated_data.pop("followup_questions", [])
        lesson = Lesson.objects.create(**validated_data)
        for q_data in questions_data:
            opts = q_data.pop("options", [])
            question = FollowUpQuestion.objects.create(lesson=lesson, **q_data)
            for o_data in opts:
                FollowUpOption.objects.create(question=question, **o_data)
        return lesson

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("followup_questions", [])
        instance.title    = validated_data.get("title", instance.title)
        instance.content  = validated_data.get("content", instance.content)
        instance.order    = validated_data.get("order", instance.order)
        instance.is_free  = validated_data.get("is_free", instance.is_free)
        instance.video    = validated_data.get("video", instance.video)
        instance.save()

        if questions_data is not None:
            instance.followup_questions.all().delete()
            for q_data in questions_data:
                opts = q_data.pop("options", [])
                question = FollowUpQuestion.objects.create(lesson=instance, **q_data)
                for o_data in opts:
                    FollowUpOption.objects.create(question=question, **o_data)

        return instance


#
# ─── QuizOptionSerializer ──────────────────────────────────────────────────────────
#
class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ["id", "label", "text", "is_correct"]
        read_only_fields = ["id"]


#
# ─── QuizQuestionSerializer ────────────────────────────────────────────────────────
#
class QuizQuestionSerializer(serializers.ModelSerializer):
    options        = QuizOptionSerializer(many=True)
    solution_text  = serializers.CharField()

    class Meta:
        model = QuizQuestion
        fields = [
            "id",
            "question_text",
            "solution_text",
            "allow_multiple",
            "options"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        opts_data = validated_data.pop("options", [])
        question = QuizQuestion.objects.create(**validated_data)
        for opt in opts_data:
            QuizOption.objects.create(question=question, **opt)
        return question

    def update(self, instance, validated_data):
        opts_data = validated_data.pop("options", [])
        instance.question_text  = validated_data.get("question_text", instance.question_text)
        instance.solution_text  = validated_data.get("solution_text", instance.solution_text)
        instance.allow_multiple = validated_data.get("allow_multiple", instance.allow_multiple)
        instance.save()

        if opts_data is not None:
            instance.options.all().delete()
            for o_data in opts_data:
                QuizOption.objects.create(question=instance, **o_data)
        return instance


#
# ─── QuizSerializer ────────────────────────────────────────────────────────────────
#
class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        quiz = Quiz.objects.create(**validated_data)
        for q_data in questions_data:
            opts = q_data.pop("options", [])
            question = QuizQuestion.objects.create(quiz=quiz, **q_data)
            for o_data in opts:
                QuizOption.objects.create(question=question, **o_data)
        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", [])
        instance.title = validated_data.get("title", instance.title)
        instance.save()

        if questions_data is not None:
            instance.questions.all().delete()
            for q_data in questions_data:
                opts = q_data.pop("options", [])
                question = QuizQuestion.objects.create(quiz=instance, **q_data)
                for o_data in opts:
                    QuizOption.objects.create(question=question, **o_data)
        return instance


#
# ─── ExamProjectSerializer ────────────────────────────────────────────────────────
#
class ExamProjectSerializer(serializers.ModelSerializer):
    student          = serializers.CharField(read_only=True, source="student.username")
    certificate_file = serializers.FileField(read_only=True)

    class Meta:
        model = ExamProject
        fields = [
            "id",
            "course",
            "student",
            "submission_file",
            "submitted_at",
            "score",
            "is_approved",
            "certificate_file",
        ]
        read_only_fields = ["id", "student", "submitted_at", "score", "is_approved", "certificate_file"]

    def create(self, validated_data):
        return super().create(validated_data)


#
# ─── OrderSerializer ───────────────────────────────────────────────────────────────
#
class OrderSerializer(serializers.ModelSerializer):
    student = serializers.CharField(read_only=True, source="student.username")
    course  = serializers.CharField(read_only=True, source="course.title")

    class Meta:
        model = Order
        fields = [
            "id",
            "student",
            "course",
            "amount",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "student", "status", "transaction_id", "created_at", "updated_at"]
