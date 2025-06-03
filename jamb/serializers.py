# jamb/serializers.py

from rest_framework import serializers
from .models import JAMBSubject, JAMBQuestion, Strategy

class JAMBSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = JAMBSubject
        fields = ("id", "name", "slug", "topics", "duration")


class JAMBQuestionSerializer(serializers.ModelSerializer):
    """
    This serializer now exposes the four option fields and the single-letter correct_choice.
    """
    class Meta:
        model = JAMBQuestion
        fields = (
            "id",
            "subject",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_choice",
        )
        read_only_fields = ("id",)


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ("id", "category", "content")
        read_only_fields = ("id",)
