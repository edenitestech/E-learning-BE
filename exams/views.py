# exams/views.py

from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ExamSubject, PastQuestion, PastOption
from .serializers import (
    ExamSubjectSerializer,
    PastQuestionSerializer,
    QuizInputSerializer
)

# ─── Helper: Letter grade from percent ──────────────────────────────────────────────
def _letter_grade(percent_score: float) -> str:
    if percent_score >= 90:
        return "A"
    if percent_score >= 80:
        return "B"
    if percent_score >= 70:
        return "C"
    if percent_score >= 60:
        return "D"
    if percent_score >= 50:
        return "E"
    return "F"


# ─── ExamSubjectViewSet ─────────────────────────────────────────────────────────────
class ExamSubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for ExamSubject (subjects like Math, English, etc.).
    """
    queryset = ExamSubject.objects.all().order_by("name")
    serializer_class = ExamSubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = []  # add e.g. SearchFilter if desired
    search_fields = ["name"]


# ─── PastQuestionViewSet ────────────────────────────────────────────────────────────
class PastQuestionViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for PastQuestion, plus:
      - GET/POST /subjects/
      - POST /quiz/
      - POST /practice/
    """
    queryset = PastQuestion.objects.all().order_by("-year")
    serializer_class = PastQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["exam_type", "year", "subject__slug"]
    search_fields = ["subject__name"]

    # Nested CRUD on ExamSubject
    @action(detail=False, methods=["get"], url_path="subjects", permission_classes=[permissions.AllowAny])
    def list_subjects(self, request):
        subs = ExamSubject.objects.all()
        serializer = ExamSubjectSerializer(subs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="subjects", permission_classes=[permissions.IsAuthenticated])
    def create_subject(self, request):
        serializer = ExamSubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Quiz mode
    @action(detail=False, methods=["post"], url_path="quiz", permission_classes=[permissions.AllowAny])
    def quiz_mode(self, request):
        top_serializer = QuizInputSerializer(data=request.data)
        top_serializer.is_valid(raise_exception=True)
        data = top_serializer.validated_data

        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        questions_qs = PastQuestion.objects.filter(
            exam_type=data["exam_type"],
            year=data["year"],
            subject=subj
        )
        q_map = {q.id: q for q in questions_qs}

        total_questions = len(q_map)
        if total_questions == 0:
            return Response(
                {"detail": "No questions found for given exam_type/year/subject."},
                status=status.HTTP_400_BAD_REQUEST
            )

        correct_count = 0
        details = []
        for ans in data["answers"]:
            qid = ans["question_id"]
            selected = ans["selected"]

            if qid not in q_map:
                continue

            question = q_map[qid]
            correct_labels = list(
                question.options.filter(is_correct=True)
                          .order_by("label")
                          .values_list("label", flat=True)
            )
            is_correct = set(selected) == set(correct_labels)
            if is_correct:
                correct_count += 1

            details.append({
                "question_id":   qid,
                "is_correct":    is_correct,
                "correct_labels": correct_labels,
                "solution_text": question.solution_text,
            })

        percent_score = round((correct_count / total_questions) * 100, 2)
        letter = _letter_grade(percent_score)

        return Response({
            "percent_score": percent_score,
            "letter_grade":  letter,
            "details":       details
        }, status=status.HTTP_200_OK)

    # Practice mode
    @action(detail=False, methods=["post"], url_path="practice", permission_classes=[permissions.AllowAny])
    def practice_mode(self, request):
        top_serializer = QuizInputSerializer(data=request.data)
        top_serializer.is_valid(raise_exception=True)
        data = top_serializer.validated_data

        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        questions_qs = PastQuestion.objects.filter(
            exam_type=data["exam_type"],
            year=data["year"],
            subject=subj
        )
        q_map = {q.id: q for q in questions_qs}

        if not q_map:
            return Response(
                {"detail": "No questions found for given exam_type/year/subject."},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        for ans in data["answers"]:
            qid = ans["question_id"]
            selected = ans["selected"]

            if qid not in q_map:
                continue

            question = q_map[qid]
            correct_labels = list(
                question.options.filter(is_correct=True)
                          .order_by("label")
                          .values_list("label", flat=True)
            )
            is_correct = set(selected) == set(correct_labels)

            results.append({
                "question_id":   qid,
                "is_correct":    is_correct,
                "correct_labels": correct_labels,
                "solution_text": question.solution_text,
            })

        return Response(results, status=status.HTTP_200_OK)


# ─── SubscriptionViewSet ────────────────────────────────────────────────────────────
class SubscriptionViewSet(viewsets.ViewSet):
    """
    GET /api/exams/subscriptions/
    Lists exam subscription fees configured in settings.EXAM_SUBSCRIPTION_FEES.
    """
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        fees = getattr(settings, "EXAM_SUBSCRIPTION_FEES", {})
        data = [{"exam_type": exam, "fee": fee} for exam, fee in fees.items()]
        return Response(data, status=status.HTTP_200_OK)
