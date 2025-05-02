from rest_framework import serializers
from .models import Lesson, Question

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "video", "video_url", "created_at"]
        read_only_fields = ["id", "created_at"]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        # Not expose the correct_choice here,
        # frontend will call /answer/ to check
        fields = ["id", "lesson", "text", "choices"]
