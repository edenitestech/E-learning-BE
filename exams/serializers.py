# exams/serializers.py

from rest_framework import serializers
from .models import PastQuestion

class PastQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastQuestion
        fields = ["id", "exam_type", "year", "subject", "question_text", "solution_text"]
