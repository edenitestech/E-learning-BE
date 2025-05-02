from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Lesson, Question
from .serializers import LessonSerializer, QuestionSerializer
# Create your views here.

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # filter by course via ?course=ID
    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get("course")
        return qs.filter(course_id=course_id) if course_id else qs

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
