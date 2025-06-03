from rest_framework import serializers
from .models import Lesson, Question, Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "label", "text", "is_correct"]
        extra_kwargs = {
            "label": {"required": True},
            "text": {"required": True},
            "is_correct": {"required": True},
        }


class QuestionSerializer(serializers.ModelSerializer):
    # Nest options under each question
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "lesson",
            "text",
            "allow_multiple",
            "explanation",
            "options",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "text": {"required": True},
            "allow_multiple": {"required": True},
            "explanation": {"required": True},
        }

    def create(self, validated_data):
        # Pop out nested options data
        options_data = validated_data.pop("options", [])
        question = Question.objects.create(**validated_data)
        # Create Option rows for this question
        for opt_data in options_data:
            Option.objects.create(question=question, **opt_data)
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None)

        # Update simple fields
        instance.text = validated_data.get("text", instance.text)
        instance.allow_multiple = validated_data.get("allow_multiple", instance.allow_multiple)
        instance.explanation = validated_data.get("explanation", instance.explanation)
        instance.save()

        if options_data is not None:
            # Delete all existing options and recreate
            instance.options.all().delete()
            for opt_data in options_data:
                Option.objects.create(question=instance, **opt_data)

        return instance


class LessonSerializer(serializers.ModelSerializer):
    # List questions (read‐only) when fetching a lesson
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "title",
            "video",
            "is_free",
            "created_at",
            "questions",
        ]
        read_only_fields = ["id", "created_at"]
