# exams/views.py
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from courses.views import IsInstructor

from .models import ExamSubject, PastQuestion
from .serializers import ExamSubjectSerializer, PastQuestionSerializer, QuizInputSerializer

def _letter_grade(pct: float) -> str:
    return (
        "A" if pct>=90 else
        "B" if pct>=80 else
        "C" if pct>=70 else
        "D" if pct>=60 else
        "E" if pct>=50 else "F"
    )

class ExamSubjectViewSet(viewsets.ModelViewSet):
    queryset         = ExamSubject.objects.all().order_by("name")
    serializer_class = ExamSubjectSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class PastQuestionViewSet(viewsets.ModelViewSet):
    queryset         = PastQuestion.objects.all().order_by("-year")
    serializer_class = PastQuestionSerializer
    filterset_fields = ["exam_type", "year", "subject__slug"]
    search_fields    = ["subject__name"]

    def get_permissions(self):
        # anyone can list/retrieve or run quiz/practice
        if self.action in ["list", "retrieve", "quiz_mode", "practice_mode", "list_subjects", "subscriptions"]:
            return [AllowAny()]
        # only authenticated can create/update/delete questions or subjects
        if self.action in ["create", "update", "partial_update", "destroy", "create_subject"]:
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=["get","post"], url_path="subjects")
    def list_subjects(self, request):
        if request.method=="GET":
            subs = ExamSubject.objects.all()
            return Response(ExamSubjectSerializer(subs, many=True).data)
        ser = ExamSubjectSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="quiz")
    def quiz_mode(self, request):
        top = QuizInputSerializer(data=request.data)
        top.is_valid(raise_exception=True)
        data = top.validated_data
        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        qs   = PastQuestion.objects.filter(exam_type=data["exam_type"], year=data["year"], subject=subj)
        qmap = {q.id:q for q in qs}
        total = len(qmap)
        if total==0:
            return Response({"detail":"No questions found."}, status=status.HTTP_400_BAD_REQUEST)
        correct, details = 0, []
        for ans in data["answers"]:
            q = qmap.get(ans["question_id"])
            if not q: continue
            correct_labels = list(q.options.filter(is_correct=True).values_list("label", flat=True))
            is_corr = set(ans["selected"]) == set(correct_labels)
            if is_corr: correct+=1
            details.append({
                "question_id":   q.id,
                "is_correct":    is_corr,
                "correct_labels": correct_labels,
                "solution_text": q.solution_text,
            })
        pct = round(correct/total*100,2)
        return Response({
            "percent_score": pct,
            "letter_grade":  _letter_grade(pct),
            "details":       details
        })

    @action(detail=False, methods=["post"], url_path="practice")
    def practice_mode(self, request):
        top = QuizInputSerializer(data=request.data)
        top.is_valid(raise_exception=True)
        data = top.validated_data
        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])
        qs   = PastQuestion.objects.filter(exam_type=data["exam_type"], year=data["year"], subject=subj)
        qmap = {q.id:q for q in qs}
        if not qmap:
            return Response({"detail":"No questions found."}, status=status.HTTP_400_BAD_REQUEST)
        results = []
        for ans in data["answers"]:
            q = qmap.get(ans["question_id"])
            if not q: continue
            correct_labels = list(q.options.filter(is_correct=True).values_list("label", flat=True))
            is_corr = set(ans["selected"])==set(correct_labels)
            results.append({
                "question_id":   q.id,
                "is_correct":    is_corr,
                "correct_labels": correct_labels,
                "solution_text": q.solution_text,
            })
        return Response(results)

    @action(detail=False, methods=["get"], url_path="subscriptions", permission_classes=[AllowAny])
    def subscriptions(self, request):
        fees = getattr(settings, "EXAM_SUBSCRIPTION_FEES", {})
        return Response([{"exam_type":k,"fee":v} for k,v in fees.items()])
