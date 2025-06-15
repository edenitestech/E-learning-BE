from rest_framework import serializers
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
    category   = serializers.SlugRelatedField(slug_field="name", queryset=Category.objects.all())
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
# ─── FollowUpOption & Question Serializers ─────────────────────────────────────────
#
class FollowUpOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpOption
        fields = ["id", "label", "text", "is_correct"]
        read_only_fields = ["id"]


class FollowUpQuestionSerializer(serializers.ModelSerializer):
    options       = FollowUpOptionSerializer(many=True)
    solution_text = serializers.CharField()

    class Meta:
        model = FollowUpQuestion
        fields = ["id", "question_text", "solution_text", "allow_multiple", "options"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        opts = validated_data.pop("options", [])
        q = FollowUpQuestion.objects.create(**validated_data)
        for o in opts:
            FollowUpOption.objects.create(question=q, **o)
        return q

    def update(self, instance, validated_data):
        opts = validated_data.pop("options", [])
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if opts is not None:
            instance.options.all().delete()
            for o in opts:
                FollowUpOption.objects.create(question=instance, **o)
        return instance


#
# ─── LessonSerializer ─────────────────────────────────────────────────────────────
#
class LessonSerializer(serializers.ModelSerializer):
    followup_questions = FollowUpQuestionSerializer(many=True, required=False)
    video              = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = [
            "id", "order", "title", "content", "video", "is_free",
            "followup_questions", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        questions = validated_data.pop("followup_questions", [])
        lesson = Lesson.objects.create(**validated_data)
        for q in questions:
            opts = q.pop("options", [])
            fq = FollowUpQuestion.objects.create(lesson=lesson, **q)
            for o in opts:
                FollowUpOption.objects.create(question=fq, **o)
        return lesson

    def update(self, instance, validated_data):
        questions = validated_data.pop("followup_questions", [])
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if questions is not None:
            instance.followup_questions.all().delete()
            for q in questions:
                opts = q.pop("options", [])
                fq = FollowUpQuestion.objects.create(lesson=instance, **q)
                for o in opts:
                    FollowUpOption.objects.create(question=fq, **o)
        return instance


#
# ─── QuizOption & Question Serializers ────────────────────────────────────────────
#
class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ["id", "label", "text", "is_correct"]
        read_only_fields = ["id"]


class QuizQuestionSerializer(serializers.ModelSerializer):
    options       = QuizOptionSerializer(many=True)
    solution_text = serializers.CharField()

    class Meta:
        model = QuizQuestion
        fields = ["id", "question_text", "solution_text", "allow_multiple", "options"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        opts = validated_data.pop("options", [])
        qq = QuizQuestion.objects.create(**validated_data)
        for o in opts:
            QuizOption.objects.create(question=qq, **o)
        return qq

    def update(self, instance, validated_data):
        opts = validated_data.pop("options", [])
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if opts is not None:
            instance.options.all().delete()
            for o in opts:
                QuizOption.objects.create(question=instance, **o)
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
        qs_data = validated_data.pop("questions", [])
        quiz = Quiz.objects.create(**validated_data)
        for q in qs_data:
            opts = q.pop("options", [])
            qq = QuizQuestion.objects.create(quiz=quiz, **q)
            for o in opts:
                QuizOption.objects.create(question=qq, **o)
        return quiz

    def update(self, instance, validated_data):
        qs_data = validated_data.pop("questions", [])
        instance.title = validated_data.get("title", instance.title)
        instance.save()
        if qs_data is not None:
            instance.questions.all().delete()
            for q in qs_data:
                opts = q.pop("options", [])
                qq = QuizQuestion.objects.create(quiz=instance, **q)
                for o in opts:
                    QuizOption.objects.create(question=qq, **o)
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
            "id", "course", "student", "submission_file",
            "submitted_at", "score", "is_approved", "certificate_file"
        ]
        read_only_fields = [
            "id", "student", "submitted_at", "score", "is_approved", "certificate_file"
        ]


#
# ─── OrderSerializer ───────────────────────────────────────────────────────────────
#
class OrderSerializer(serializers.ModelSerializer):
    student = serializers.CharField(read_only=True, source="student.username")
    course  = serializers.CharField(read_only=True, source="course.title")

    class Meta:
        model = Order
        fields = [
            "id", "student", "course", "amount",
            "status", "transaction_id", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "student", "status", "transaction_id", "created_at", "updated_at"
        ]
