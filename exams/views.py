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


#
# ─── Helper: Letter grade from percent ──────────────────────────────────────────────
#
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


#
# ─── PastQuestionViewSet ────────────────────────────────────────────────────────────
#
class PastQuestionViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for PastQuestion, plus two custom actions:
      - POST /past-questions/quiz/     (returns a % score, letter grade, per‐question results)
      - POST /past-questions/practice/ (returns per‐question correctness + solution immediately)
    """
    queryset         = PastQuestion.objects.all().order_by("-year")
    serializer_class = PastQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["exam_type", "year", "subject__slug"]
    search_fields    = ["subject__name"]

    #
    # ─── Nested CRUD on ExamSubject (if you want to treat subjects as part of this ViewSet) ─
    #
    @action(detail=False, methods=["get"], url_path="subjects", permission_classes=[permissions.AllowAny])
    def list_subjects(self, request):
        """
        GET /api/exams/past-questions/subjects/
        Lists all ExamSubject records.
        """
        subs = ExamSubject.objects.all()
        serializer = ExamSubjectSerializer(subs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="subjects", permission_classes=[permissions.IsAuthenticated])
    def create_subject(self, request):
        """
        POST /api/exams/past-questions/subjects/
        Body: { "name": "Physics" }
        """
        serializer = ExamSubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #
    # ─── QUIZ MODE ────────────────────────────────────────────────────────────────────
    #
    @action(detail=False, methods=["post"], url_path="quiz", permission_classes=[permissions.AllowAny])
    def quiz_mode(self, request):
        """
        POST /api/exams/past-questions/quiz/
        Input body example:
        {
          "exam_type":  "JAMB",
          "year":       2024,
          "subject_slug": "mathematics",
          "answers": [
            { "question_id": 101, "selected": ["B"] },
            { "question_id": 102, "selected": ["A","C"] }
          ]
        }
        Returns:
        {
          "percent_score": 85.0,
          "letter_grade": "B",
          "details": [
            { "question_id": 101, "is_correct": true,  "correct_labels": ["B"],     "solution_text": "…” },
            { "question_id": 102, "is_correct": false, "correct_labels": ["A","C"], "solution_text": "…” }
          ]
        }
        """
        # Validate top-level input
        top_serializer = QuizInputSerializer(data=request.data)
        top_serializer.is_valid(raise_exception=True)
        data = top_serializer.validated_data

        # Lookup the subject
        subj = get_object_or_404(ExamSubject, slug=data["subject_slug"])

        # Fetch all questions matching exam_type, year, subject
        questions_qs = PastQuestion.objects.filter(
            exam_type=data["exam_type"],
            year=data["year"],
            subject=subj
        )

        # Map of question_id → PastQuestion instance
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
            qid      = ans["question_id"]
            selected = ans["selected"]  # a list of labels, e.g. ["A"] or ["B","C"]

            if qid not in q_map:
                # Skip any answer for a non‐existent or out‐of‐scope question:
                continue

            question = q_map[qid]
            # Compute the correct labels set for this question:
            correct_labels = list(
                question.options.filter(is_correct=True)
                          .order_by("label")
                          .values_list("label", flat=True)
            )

            # Compare (order does not matter; use sets)
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

    #
    # ─── PRACTICE MODE ─────────────────────────────────────────────────────────────────
    #
    @action(detail=False, methods=["post"], url_path="practice", permission_classes=[permissions.AllowAny])
    def practice_mode(self, request):
        """
        POST /api/exams/past-questions/practice/
        Input identically structured to /quiz/, but returns per‐question feedback only.
        Example response:
        [
          {
            "question_id": 101,
            "is_correct":  true,
            "correct_labels": ["B"],
            "solution_text": "…" 
          },
          {
            "question_id": 102,
            "is_correct":  false,
            "correct_labels": ["A","C"],
            "solution_text": "…" 
          }
        ]
        """
        # Validate input
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
            qid      = ans["question_id"]
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
