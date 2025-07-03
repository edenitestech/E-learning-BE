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

class PastQuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD + drill-down helpers + quiz/practice endpoints.
    """
    queryset          = PastQuestion.objects.all().order_by("-year")
    serializer_class  = PastQuestionSerializer
    filterset_fields  = ["exam_type", "year", "subject__slug"]
    search_fields     = ["subject__name"]

    def get_permissions(self):
        public = ["list","retrieve","types","subjects","years","quiz_mode","practice_mode"]
        if self.action in public:
            return [AllowAny()]
        if self.action in ["create","update","partial_update","destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=["get"], url_path="types")
    def types(self, request):
        vals = (
            PastQuestion.objects.values_list("exam_type", flat=True)
                                 .distinct()
                                 .order_by("exam_type")
        )
        return Response(list(vals))

    @action(detail=False, methods=["get", "post"], url_path="subjects")
    def subjects(self, request):
        """
        GET  /api/exams/past-questions/subjects/?exam_type=JAMB
             → Returns subjects having questions of that exam_type.
             → If no exam_type param, returns all subjects.

        POST /api/exams/past-questions/subjects/
             → Create a new subject.
        """
        if request.method == "GET":
            exam_type = request.query_params.get("exam_type")
            qs = ExamSubject.objects.all()
            if exam_type:
                qs = qs.filter(past_questions__exam_type=exam_type).distinct()
            serializer = ExamSubjectSerializer(qs, many=True)
            return Response(serializer.data)

        # POST: create a new ExamSubject
        serializer = ExamSubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=["get"], url_path="years")
    def years(self, request):
        """
        GET /api/exams/past-questions/years/?exam_type=…&subject_slug=…
        """
        et   = request.query_params.get("exam_type")
        slug = request.query_params.get("subject_slug")
        qs = PastQuestion.objects.all()
        if et:   qs = qs.filter(exam_type=et)
        if slug: qs = qs.filter(subject__slug=slug)
        yrs = qs.values_list("year", flat=True).distinct().order_by("year")
        return Response(list(yrs))

    @action(detail=False, methods=["post"], url_path="quiz")
    def quiz_mode(self, request):
        top = QuizInputSerializer(data=request.data)
        top.is_valid(raise_exception=True)
        data = top.validated_data

        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        qs   = PastQuestion.objects.filter(
            exam_type=data["exam_type"],
            year=data["year"],
            subject=subj
        )
        mapping = {q.id:q for q in qs}
        total   = len(mapping)
        if total == 0:
            return Response({"detail":"No questions found."},
                            status=status.HTTP_400_BAD_REQUEST)

        correct = 0
        details = []
        for ans in data["answers"]:
            q = mapping.get(ans["question_id"])
            if not q: continue
            right_labels = list(
                q.options.filter(is_correct=True)
                         .order_by("label")
                         .values_list("label", flat=True)
            )
            ok = set(ans["selected"])==set(right_labels)
            if ok: correct += 1
            details.append({
                "question_id":    q.id,
                "is_correct":     ok,
                "correct_labels": right_labels,
                "solution_text":  q.solution_text,
            })

        percent = round(correct/total*100,2)
        return Response({
            "percent_score": percent,
            "letter_grade":  _letter_grade(percent),
            "details":       details,
        })

    @action(detail=False, methods=["post"], url_path="practice")
    def practice_mode(self, request):
        top = QuizInputSerializer(data=request.data)
        top.is_valid(raise_exception=True)
        data = top.validated_data

        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        qs   = PastQuestion.objects.filter(
            exam_type=data["exam_type"],
            year=data["year"],
            subject=subj
        )
        mapping = {q.id:q for q in qs}
        if not mapping:
            return Response({"detail":"No questions found."},
                            status=status.HTTP_400_BAD_REQUEST)

        out = []
        for ans in data["answers"]:
            q = mapping.get(ans["question_id"])
            if not q: continue
            right_labels = list(
                q.options.filter(is_correct=True)
                         .order_by("label")
                         .values_list("label", flat=True)
            )
            ok = set(ans["selected"])==set(right_labels)
            out.append({
                "question_id":    q.id,
                "is_correct":     ok,
                "correct_labels": right_labels,
                "solution_text":  q.solution_text,
            })
        return Response(out)

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
