# jamb/serializers.py

from rest_framework import serializers
from .models import JAMBSubject, JAMBQuestion, Strategy

class JAMBQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JAMBQuestion
        fields = ["id", "question_text", "options", "correct_index"]


class JAMBSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = JAMBSubject
        fields = ["id", "name", "slug", "topics", "duration"]


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ["id", "category", "content"]
