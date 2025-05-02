from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Enrollment, LessonProgress, Answer
from .serializers import (
    EnrollmentSerializer,
    LessonProgressSerializer,
    AnswerSerializer,
)

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # student only sees their own enrollments
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class LessonProgressViewSet(viewsets.ModelViewSet):
    
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only progress for this student
        return LessonProgress.objects.filter(
            enrollment__student=self.request.user
        )

class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Answer.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        # auto‑compute correctness
        ans = serializer.save(student=self.request.user)
        ans.is_correct = (ans.selected == ans.question.correct_choice)
        ans.save()
        return super().perform_create(serializer)
