from rest_framework import viewsets, permissions
from .models import Enrollment, LessonProgress, Answer
from .serializers import (
    EnrollmentSerializer,
    LessonProgressSerializer,
    AnswerSerializer,
)

# ─── Note: We no longer import `content.models.Option` because
#          the “options” are now in the `courses` app (FollowUpOption/QuizOption).

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
        # Determine correctness by looking up the proper Option in `courses`:
        from courses.models import FollowUpOption, QuizOption

        # If this Answer is for a FollowUpQuestion:
        try:
            opt = FollowUpOption.objects.get(question=ans.question, label=ans.selected)
            ans.is_correct = opt.is_correct
        except FollowUpOption.DoesNotExist:
            # Otherwise, check if it might be a QuizOption:
            try:
                opt = QuizOption.objects.get(question=ans.question, label=ans.selected)
                ans.is_correct = opt.is_correct
            except QuizOption.DoesNotExist:
                ans.is_correct = False

        ans.save()
        return super().perform_create(serializer)
