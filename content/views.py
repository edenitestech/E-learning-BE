from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Lesson, Question
from .serializers import LessonSerializer, QuestionSerializer
from rest_framework.exceptions import PermissionDenied
from enrollments.models import Enrollment
# Create your views here.

class IsEnrolledOrFreePermission(permissions.BasePermission):
    """
    Allows access if the lesson is marked `is_free=True` or
    if the requesting user is enrolled in the parent course.
    """
    def has_object_permission(self, request, view, obj):
        # obj may be a Lesson or a Question
        lesson = obj if isinstance(obj, Lesson) else obj.lesson

        # free preview?
        if lesson.is_free or lesson.course.price == 0:
            return True

        # check enrollment
        return Enrollment.objects.filter(
            student=request.user, course=lesson.course
        ).exists()

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # filter by course via ?course=ID
    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get("course")
        return qs.filter(course_id=course_id) if course_id else qs

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()

        # free lesson? always allowed
        if lesson.is_free:
            return super().retrieve(request, *args, **kwargs)

        # else check if user is enrolled
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=lesson.course
        ).exists()
        if not is_enrolled:
            raise PermissionDenied("You must purchase the course for full access.")
        return super().retrieve(request, *args, **kwargs)
 
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        lesson_id = self.request.query_params.get("lesson")
        return qs.filter(lesson_id=lesson_id) if lesson_id else qs

    @action(detail=True, methods=["post"], url_path="answer")
    def submit_answer(self, request, pk=None):
        question = self.get_object()
        selected = request.data.get("selected")
        is_correct = (selected == question.correct_choice)
        # optionally save Answer instance here…
        return Response({"is_correct": is_correct})

    @action(detail=True, methods=["get"], url_path="explanation")
    def explanation(self, request, pk=None):
        question = self.get_object()
        return Response({"explanation": question.explanation})
