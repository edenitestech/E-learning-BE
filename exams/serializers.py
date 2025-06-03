# exams/serializers.py

from rest_framework import serializers
from .models import PastQuestion, Option, Subject

#
# 1. Existing serializers for read/write PastQuestion + options
#

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "label", "text", "is_correct"]


class PastQuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

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


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "slug"]
        read_only_fields = ["id"]


#
# 2. Serializer for "Practice mode": posting one answer at a time
#

class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_label = serializers.ChoiceField(choices=[("A","A"),("B","B"),("C","C"),("D","D")])

    def validate_question_id(self, value):
        try:
            PastQuestion.objects.get(pk=value)
        except PastQuestion.DoesNotExist:
            raise serializers.ValidationError("Invalid question_id.")
        return value



# 3. Serializer for "Quiz mode": posting multiple answers at once

class QuizAnswerItemSerializer(serializers.Serializer):
    question_id    = serializers.IntegerField()
    selected_label = serializers.ChoiceField(choices=[("A","A"),("B","B"),("C","C"),("D","D")])

    def validate_question_id(self, value):
        try:
            PastQuestion.objects.get(pk=value)
        except PastQuestion.DoesNotExist:
            raise serializers.ValidationError("Invalid question_id in quiz submission.")
        return value


class QuizSubmissionSerializer(serializers.Serializer):
    exam_type = serializers.ChoiceField(choices=PastQuestion.EXAM_CHOICES)
    year      = serializers.IntegerField()
    subject_id = serializers.IntegerField()
    answers   = QuizAnswerItemSerializer(many=True)

    def validate_subject_id(self, value):
        from .models import Subject
        try:
            Subject.objects.get(pk=value)
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Invalid subject_id.")
        return value

    def validate(self, attrs):
        # Ensure at least one answer is provided
        if not attrs.get("answers"):
            raise serializers.ValidationError("Must provide at least one answer item.")
        return attrs


# 4. Serializer for returning Quiz results

class QuizResultItemSerializer(serializers.Serializer):
    question_id    = serializers.IntegerField()
    question_text  = serializers.CharField()
    selected_label = serializers.CharField()
    correct_label  = serializers.CharField()
    is_correct     = serializers.BooleanField()
    solution_text  = serializers.CharField()


class QuizResultSerializer(serializers.Serializer):
    total_questions = serializers.IntegerField()
    correct_count   = serializers.IntegerField()
    score_percentage = serializers.FloatField()
    grade            = serializers.CharField()
    details         = QuizResultItemSerializer(many=True)
