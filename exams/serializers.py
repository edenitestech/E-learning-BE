# exams/serializers.py
from rest_framework import serializers
from .models import (
    ExamSubject,
    PastQuestion,
    PastOption
)


#
# ─── ExamSubjectSerializer ─────────────────────────────────────────────────────────
#
class ExamSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubject
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


#
# ─── PastOptionSerializer ──────────────────────────────────────────────────────────
#
class PastOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastOption
        fields = ["id", "label", "text", "is_correct"]
        read_only_fields = ["id"]


#
# ─── PastQuestionSerializer ────────────────────────────────────────────────────────
#
class PastQuestionSerializer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=ExamSubject.objects.all()
    )
    options = PastOptionSerializer(many=True)

    class Meta:
        model = PastQuestion
        fields = [
            "id",
            "exam_type",
            "year",
            "subject",
            "question_text",
            "solution_text",
            "allow_multiple",
            "options",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        opts_data = validated_data.pop("options", [])
        question = PastQuestion.objects.create(**validated_data)
        for o in opts_data:
            PastOption.objects.create(question=question, **o)
        return question

    def update(self, instance, validated_data):
        opts_data = validated_data.pop("options", [])
        instance.exam_type      = validated_data.get("exam_type", instance.exam_type)
        instance.year           = validated_data.get("year", instance.year)
        instance.subject        = validated_data.get("subject", instance.subject)
        instance.question_text  = validated_data.get("question_text", instance.question_text)
        instance.solution_text  = validated_data.get("solution_text", instance.solution_text)
        instance.allow_multiple = validated_data.get("allow_multiple", instance.allow_multiple)
        instance.save()

        # Replace ALL options if provided:
        instance.options.all().delete()
        for o_data in opts_data:
            PastOption.objects.create(question=instance, **o_data)
        return instance


#
# ─── Serializer for incoming quiz/practice answers ─────────────────────────────────
#
class QuestionAttemptSerializer(serializers.Serializer):
    """
    Used by both 'quiz' and 'practice' endpoints.
    Each entry in 'answers' must have:
      - question_id : ID of PastQuestion
      - selected    : list of one or more labels, e.g. ["A"] or ["B","C"]
    """
    question_id = serializers.IntegerField()
    selected    = serializers.ListField(
        child=serializers.ChoiceField(choices=[(c, c) for c in "ABCD"]),
        allow_empty=False
    )


class QuizInputSerializer(serializers.Serializer):
    """
    The top‐level input for /past-questions/quiz/ or /past-questions/practice/
    """
    exam_type    = serializers.ChoiceField(choices=PastQuestion.EXAM_CHOICES)
    year         = serializers.IntegerField()
    subject_slug = serializers.SlugField()
    answers      = QuestionAttemptSerializer(many=True)
