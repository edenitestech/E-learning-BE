# exams/views.py

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import PastQuestion, Subject, Option
from .serializers import (
    PastQuestionSerializer,
    SubjectSerializer,
    AnswerSubmissionSerializer,
    QuizSubmissionSerializer,
    QuizResultSerializer,
    QuizResultItemSerializer,
)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]


class PastQuestionViewSet(viewsets.ModelViewSet):
    queryset = PastQuestion.objects.all().order_by("-year")
    serializer_class = PastQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    filterset_fields = ["exam_type", "year", "subject"]
    search_fields = ["question_text"]
    permission_classes = [permissions.AllowAny]

    #
    # 1) PRACTICE MODE:
    #
    @action(detail=False, methods=["POST"], url_path="practice", permission_classes=[permissions.AllowAny])
    def practice(self, request):
        """
        Accept a single question_id + selected_label → return immediate feedback:
        {
          "question_id": int,
          "selected_label": "A"/"B"/"C"/"D",
          "is_correct": true/false,
          "correct_label": "B",
          "solution_text": "…" 
        }
        """
        serializer = AnswerSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qid = serializer.validated_data["question_id"]
        chosen = serializer.validated_data["selected_label"]

        question = get_object_or_404(PastQuestion, pk=qid)
        # Find the chosen Option
        try:
            selected_option = question.options.get(label=chosen)
        except Option.DoesNotExist:
            return Response(
                {"detail": "Selected label not found for this question."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determine correctness
        is_correct = selected_option.is_correct

        # Find the correct label (there could be multiple if allow_multiple=True)
        correct_options = question.options.filter(is_correct=True)
        # If multiple are correct, join them by comma
        correct_labels = ",".join([opt.label for opt in correct_options])

        return Response({
            "question_id": qid,
            "selected_label": chosen,
            "is_correct": is_correct,
            "correct_label": correct_labels,
            "solution_text": question.solution_text,
        })

    #
    # 2) QUIZ MODE:
    #
    @action(detail=False, methods=["POST"], url_path="quiz", permission_classes=[permissions.IsAuthenticated])
    def quiz(self, request):
        """
        Accept: { exam_type, year, subject_id, answers: [{question_id, selected_label}, …] }
        → Return: { total_questions, correct_count, score_percentage, grade, details: [ … ] }
        """
        quiz_serializer = QuizSubmissionSerializer(data=request.data)
        quiz_serializer.is_valid(raise_exception=True)
        data = quiz_serializer.validated_data

        exam_type = data["exam_type"]
        year = data["year"]
        subject = get_object_or_404(Subject, pk=data["subject_id"])
        submitted_answers = data["answers"]  # list of {question_id, selected_label}

        # 1) Fetch all PastQuestion objects matching filter
        questions_qs = PastQuestion.objects.filter(
            exam_type=exam_type,
            year=year,
            subject=subject
        )
        total_questions = questions_qs.count()

        # 2) Build a dict: qid → PastQuestion instance for fast lookup
        questions_by_id = {q.id: q for q in questions_qs}

        # 3) Tally correct answers
        correct_count = 0
        details = []

        for answer_item in submitted_answers:
            qid = answer_item["question_id"]
            chosen_label = answer_item["selected_label"]

            question = questions_by_id.get(qid)
            if question is None:
                # Submitted an ID that doesn't match the filter set
                details.append({
                    "question_id": qid,
                    "question_text": "",
                    "selected_label": chosen_label,
                    "correct_label": "",
                    "is_correct": False,
                    "solution_text": "Question not found in specified exam/year/subject.",
                })
                continue

            # Find the selected Option
            try:
                selected_option = question.options.get(label=chosen_label)
                is_correct = selected_option.is_correct
            except Option.DoesNotExist:
                is_correct = False  # label not found

            if is_correct:
                correct_count += 1

            # Find all correct labels (comma‐separated if multiple)
            correct_opts = question.options.filter(is_correct=True)
            correct_labels = ",".join([opt.label for opt in correct_opts])

            details.append({
                "question_id": qid,
                "question_text": question.question_text,
                "selected_label": chosen_label,
                "correct_label": correct_labels,
                "is_correct": is_correct,
                "solution_text": question.solution_text,
            })

        # 4) Compute percentage score
        if total_questions > 0:
            score_percentage = (correct_count / total_questions) * 100.0
        else:
            score_percentage = 0.0

        # 5) Determine letter grade (standard scale)
        #    A: 90–100, B: 80–89, C: 70–79, D: 60–69, E: 50–59, F: <50
        if score_percentage >= 90:
            grade = "A"
        elif score_percentage >= 80:
            grade = "B"
        elif score_percentage >= 70:
            grade = "C"
        elif score_percentage >= 60:
            grade = "D"
        elif score_percentage >= 50:
            grade = "E"
        else:
            grade = "F"

        # 6) Package into result serializer
        result_data = {
            "total_questions": total_questions,
            "correct_count": correct_count,
            "score_percentage": round(score_percentage, 2),
            "grade": grade,
            "details": details,
        }
        result_serializer = QuizResultSerializer(result_data)
        return Response(result_serializer.data)
