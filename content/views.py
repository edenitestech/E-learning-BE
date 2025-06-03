from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Lesson, Question, Option
from .serializers import LessonSerializer, QuestionSerializer, OptionSerializer
from enrollments.models import Enrollment

class IsEnrolledOrFreePermission(permissions.BasePermission):
    """
    Allows access if the lesson is marked `is_free=True` or
    if the requesting user is enrolled in the parent course.
    """
    def has_object_permission(self, request, view, obj):
        # obj may be a Lesson or a Question
        lesson = obj if isinstance(obj, Lesson) else obj.lesson

        # If the lesson is free or the course has price 0, allow
        if lesson.is_free or lesson.course.price == 0:
            return True

        # Otherwise, check if request.user is enrolled
        return Enrollment.objects.filter(
            student=request.user, course=lesson.course
        ).exists()


class LessonViewSet(viewsets.ModelViewSet):
    queryset         = Lesson.objects.all().order_by("-created_at")
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get("course")
        return qs.filter(course_id=course_id) if course_id else qs

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        # Always allow free lessons
        if lesson.is_free or lesson.course.price == 0:
            return super().retrieve(request, *args, **kwargs)

        # Otherwise ensure the user is enrolled
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=lesson.course
        ).exists()
        if not is_enrolled:
            raise PermissionDenied("You must purchase the course for full access.")
        return super().retrieve(request, *args, **kwargs)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset         = Question.objects.all().order_by("-created_at")
    serializer_class = QuestionSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsEnrolledOrFreePermission
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        lesson_id = self.request.query_params.get("lesson")
        return qs.filter(lesson_id=lesson_id) if lesson_id else qs

    @action(detail=True, methods=["post"], url_path="answer", permission_classes=[permissions.IsAuthenticated])
    def submit_answer(self, request, pk=None):
        question = self.get_object()
        selected = request.data.get("selected")
        # Look up the Option for this question and label
        try:
            opt = question.options.get(label=selected)
            is_correct = opt.is_correct
        except Option.DoesNotExist:
            is_correct = False

        # (Optionally, you could save an Answer instance here…)
        return Response({"is_correct": is_correct})

    @action(detail=True, methods=["get"], url_path="explanation", permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def explanation(self, request, pk=None):
        question = self.get_object()
        return Response({"explanation": question.explanation})


class OptionViewSet(viewsets.ModelViewSet):
    queryset         = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.request.query_params.get("question")
        return qs.filter(question_id=question_id) if question_id else qs
