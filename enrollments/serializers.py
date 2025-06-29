# Enrollments/serializers.py
from rest_framework import serializers
from .models import Enrollment, LessonProgress, Answer

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "enrolled_at"]
        read_only_fields = ["id", "student", "enrolled_at"]


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ["id", "enrollment", "lesson", "completed"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "question", "student", "selected", "is_correct"]
        read_only_fields = ["id", "student", "is_correct"]
