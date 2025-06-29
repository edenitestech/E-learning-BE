# Enrollment/views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import Enrollment, LessonProgress, Answer
from .serializers import EnrollmentSerializer, LessonProgressSerializer, AnswerSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        # Only authenticated users may list/create their own enrollments
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.IsAuthenticated()]
        # No updates/deletes allowed except by staff
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class LessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class = LessonProgressSerializer

    def get_permissions(self):
        # Students may list/create their own progress
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.IsAuthenticated()]
        # No updates/deletes by students
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        return LessonProgress.objects.filter(enrollment__student=self.request.user)


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer

    def get_permissions(self):
        # Students may list/create their own answers
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.IsAuthenticated()]
        # No updates/deletes by students
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        return Answer.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        ans = serializer.save(student=self.request.user)
        # Auto‐grade
        from courses.models import FollowUpOption, QuizOption
        try:
            opt = FollowUpOption.objects.get(question=ans.question, label=ans.selected)
        except FollowUpOption.DoesNotExist:
            try:
                opt = QuizOption.objects.get(question=ans.question, label=ans.selected)
            except QuizOption.DoesNotExist:
                opt = None
        ans.is_correct = bool(opt and opt.is_correct)
        ans.save()
        return ans
