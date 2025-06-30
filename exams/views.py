# exams/views.py

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import ExamSubject, PastQuestion
from .serializers import (
    ExamSubjectSerializer,
    PastQuestionSerializer,
    QuizInputSerializer,
)


def _letter_grade(pct: float) -> str:
    if pct >= 90: return "A"
    if pct >= 80: return "B"
    if pct >= 70: return "C"
    if pct >= 60: return "D"
    if pct >= 50: return "E"
    return "F"


class ExamSubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for exam subjects (e.g. Mathematics, English).
    GET/HEAD/OPTIONS: public
    POST/PUT/PATCH/DELETE: authenticated users
    """
    queryset = ExamSubject.objects.all().order_by("name")
    serializer_class = ExamSubjectSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [permissions.IsAuthenticatedOrReadOnly()]


class PastQuestionViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for PastQuestion plus:
      - drill‑down helpers:
         GET  /past-questions/types/
         GET  /past-questions/subjects/?exam_type=…
         GET  /past-questions/years/?exam_type=…&subject_slug=…
      - nested CRUD on subjects via GET/POST /past-questions/subjects/
      - POST /past-questions/quiz/
      - POST /past-questions/practice/
    """
    queryset          = PastQuestion.objects.all().order_by("-year")
    serializer_class  = PastQuestionSerializer
    filterset_fields  = ["exam_type", "year", "subject__slug"]
    search_fields     = ["subject__name"]

    def get_permissions(self):
        # Public GETs and quiz/practice and drill‑down list:
        if self.action in [
            "list", "retrieve",
            "types", "subjects", "years",
            "quiz_mode", "practice_mode",
            "list_subjects"
        ]:
            return [AllowAny()]
        # Authenticated can create/update/destroy questions or subjects:
        if self.action in [
            "create", "update", "partial_update", "destroy",
            "create_subject"
        ]:
            return [permissions.IsAuthenticated()]
        # Everything else restricted to admins
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=["get"], url_path="types")
    def types(self, request):
        """
        GET /api/exams/past-questions/types/
        Returns all exam types that have at least one question.
        """
        types = (
            PastQuestion.objects
            .values_list("exam_type", flat=True)
            .distinct()
            .order_by("exam_type")
        )
        return Response(list(types))

    @action(detail=False, methods=["get"], url_path="subjects")
    def subjects(self, request):
        """
        GET /api/exams/past-questions/subjects/?exam_type=JAMB
        Returns only subjects that have questions of that exam_type.
        """
        exam_type = request.query_params.get("exam_type")
        qs = ExamSubject.objects.all()
        if exam_type:
            qs = qs.filter(pastquestion__exam_type=exam_type).distinct()
        serializer = ExamSubjectSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="years")
    def years(self, request):
        """
        GET /api/exams/past-questions/years/
          ?exam_type=JAMB&subject_slug=mathematics
        Returns only years that have questions matching those filters.
        """
        exam_type    = request.query_params.get("exam_type")
        subject_slug = request.query_params.get("subject_slug")
        qs = PastQuestion.objects.all()
        if exam_type:
            qs = qs.filter(exam_type=exam_type)
        if subject_slug:
            qs = qs.filter(subject__slug=subject_slug)
        years = qs.values_list("year", flat=True).distinct().order_by("year")
        return Response(list(years))

    @action(detail=False, methods=["get", "post"], url_path="subjects")
    def list_subjects(self, request):
        """
        GET  /api/exams/past-questions/subjects/ — list all subjects
        POST /api/exams/past-questions/subjects/ — create new subject
        """
        if request.method == "GET":
            subs = ExamSubject.objects.all()
            serializer = ExamSubjectSerializer(subs, many=True)
            return Response(serializer.data)

        # POST
        serializer = ExamSubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="quiz")
    def quiz_mode(self, request):
        """
        POST /api/exams/past-questions/quiz/
        Returns overall score, letter grade, and per‐question results.
        """
        top = QuizInputSerializer(data=request.data)
        top.is_valid(raise_exception=True)
        data = top.validated_data

        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        qs   = PastQuestion.objects.filter(
            exam_type=data["exam_type"],
            year=data["year"],
            subject=subj
        )
        qmap = {q.id: q for q in qs}
        total = len(qmap)
        if total == 0:
            return Response(
                {"detail": "No questions found for given criteria."},
                status=status.HTTP_400_BAD_REQUEST
            )

        correct = 0
        details = []
        for ans in data["answers"]:
            q = qmap.get(ans["question_id"])
            if not q:
                continue
            correct_labels = list(
                q.options.filter(is_correct=True)
                           .order_by("label")
                           .values_list("label", flat=True)
            )
            is_corr = set(ans["selected"]) == set(correct_labels)
            if is_corr:
                correct += 1
            details.append({
                "question_id":    q.id,
                "is_correct":     is_corr,
                "correct_labels": correct_labels,
                "solution_text":  q.solution_text,
            })

        percent = round(correct / total * 100, 2)
        return Response({
            "percent_score": percent,
            "letter_grade":  _letter_grade(percent),
            "details":       details,
        })

    @action(detail=False, methods=["post"], url_path="practice")
    def practice_mode(self, request):
        """
        POST /api/exams/past-questions/practice/
        Returns per‐question correctness + solution immediately.
        """
        top = QuizInputSerializer(data=request.data)
        top.is_valid(raise_exception=True)
        data = top.validated_data

        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        qs   = PastQuestion.objects.filter(
            exam_type=data["exam_type"],
            year=data["year"],
            subject=subj
        )
        qmap = {q.id: q for q in qs}
        if not qmap:
            return Response(
                {"detail": "No questions found for given criteria."},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        for ans in data["answers"]:
            q = qmap.get(ans["question_id"])
            if not q:
                continue
            correct_labels = list(
                q.options.filter(is_correct=True)
                           .order_by("label")
                           .values_list("label", flat=True)
            )
            is_corr = set(ans["selected"]) == set(correct_labels)
            results.append({
                "question_id":    q.id,
                "is_correct":     is_corr,
                "correct_labels": correct_labels,
                "solution_text":  q.solution_text,
            })
        return Response(results)


class SubscriptionViewSet(viewsets.ViewSet):
    """
    GET /exams/subscriptions/
    Returns the subscription fee for each exam type from settings.EXAM_SUBSCRIPTION_FEES.
    """
    permission_classes = [AllowAny]

    def list(self, request):
        fees = getattr(settings, "EXAM_SUBSCRIPTION_FEES", {})
        data = [{"exam_type": key, "fee": value} for key, value in fees.items()]
        return Response(data, status=status.HTTP_200_OK)
