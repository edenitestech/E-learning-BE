from rest_framework import viewsets, permissions
from .models import Enrollment, LessonProgress, Answer
from .serializers import (
    EnrollmentSerializer,
    LessonProgressSerializer,
    AnswerSerializer,
)
from content.models import Option

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class   = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # A student only sees their own enrollments
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class LessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class   = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only progress for this student
        return LessonProgress.objects.filter(
            enrollment__student=self.request.user
        )


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class   = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Answer.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        ans = serializer.save(student=self.request.user)
        # Determine correctness by looking up the Option
        try:
            opt = Option.objects.get(question=ans.question, label=ans.selected)
            ans.is_correct = opt.is_correct
        except Option.DoesNotExist:
            ans.is_correct = False
        ans.save()
        return super().perform_create(serializer)
