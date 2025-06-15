from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Category,
    Course,
    Lesson,
    FollowUpQuestion,
    FollowUpOption,
    Quiz,
    QuizQuestion,
    QuizOption,
    ExamProject,
    Order
)
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LessonSerializer,
    QuizSerializer,
    ExamProjectSerializer,
    OrderSerializer
)
from enrollments.models import Enrollment
from payment.paystack import initialize_transaction, verify_transaction  # <― centralized

#
# ─── Custom Permission ──────────────────────────────────────────────────────────────
#
class IsInstructor(permissions.BasePermission):
    """
    Only allow access if user.is_authenticated AND user.is_instructor=True
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_instructor", False)
        )


#
# ─── CategoryViewSet ────────────────────────────────────────────────────────────────
#
class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for Course Categories.
    """
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


#
# ─── CourseViewSet ──────────────────────────────────────────────────────────────────
#
class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD for Courses + nested lesson/quiz/exam endpoints + purchase/verify.
    """
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__name", "instructor__username"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_at"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    #
    # ─── Nested: lessons ───────────────────────────────────────────────────────────
    #
    @action(detail=True, methods=["get"], url_path="lessons", permission_classes=[permissions.AllowAny])
    def lessons(self, request, pk=None):
        course = self.get_object()
        qs = course.lessons.all().order_by("order")
        if not course.is_free and not request.user.is_authenticated:
            qs = qs.filter(is_free=True)
        serializer = LessonSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="lessons", permission_classes=[IsInstructor])
    def create_lesson(self, request, pk=None):
        course = self.get_object()
        data = request.data.copy()
        data["course"] = course.id
        serializer = LessonSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["put", "patch", "delete"],
        url_path=r"lessons/(?P<lesson_id>[^/.]+)",
        permission_classes=[IsInstructor]
    )
    def modify_lesson(self, request, pk=None, lesson_id=None):
        course = self.get_object()
        lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
        if request.method in ["PUT", "PATCH"]:
            partial = (request.method == "PATCH")
            serializer = LessonSerializer(lesson, data=request.data, partial=partial, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    #
    # ─── Nested: quizzes ───────────────────────────────────────────────────────────
    #
    @action(detail=True, methods=["get"], url_path="quizzes", permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def list_quizzes(self, request, pk=None):
        course = self.get_object()
        qs = course.quizzes.all().order_by("title")
        serializer = QuizSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="quizzes", permission_classes=[IsInstructor])
    def create_quiz(self, request, pk=None):
        course = self.get_object()
        data = request.data.copy()
        data["course"] = course.id
        serializer = QuizSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["put", "patch", "delete"],
        url_path=r"quizzes/(?P<quiz_id>[^/.]+)",
        permission_classes=[IsInstructor]
    )
    def modify_quiz(self, request, pk=None, quiz_id=None):
        course = self.get_object()
        quiz = get_object_or_404(Quiz, pk=quiz_id, course=course)
        if request.method in ["PUT", "PATCH"]:
            partial = (request.method == "PATCH")
            serializer = QuizSerializer(quiz, data=request.data, partial=partial, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    #
    # ─── Nested: exam projects ──────────────────────────────────────────────────────
    #
    @action(detail=True, methods=["post"], url_path="exam-project", permission_classes=[permissions.IsAuthenticated])
    def submit_exam(self, request, pk=None):
        course = self.get_object()
        data = {
            "course": course.id,
            "submission_file": request.data.get("submission_file"),
        }
        serializer = ExamProjectSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(student=request.user, course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["post"],
        url_path=r"exam-project/(?P<submission_id>[^/.]+)/approve",
        permission_classes=[IsInstructor]
    )
    def approve_exam(self, request, pk=None, submission_id=None):
        course = self.get_object()
        submission = get_object_or_404(ExamProject, pk=submission_id, course=course)
        if submission.is_approved:
            return Response({"detail": "Already approved."}, status=status.HTTP_400_BAD_REQUEST)

        score = request.data.get("score")
        cert = request.FILES.get("certificate_file")
        if score is None or cert is None:
            return Response(
                {"detail": "Both score and certificate_file are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        submission.score = score
        submission.certificate_file = cert
        submission.is_approved = True
        submission.save()
        return Response(ExamProjectSerializer(submission, context={"request": request}).data)

    #
    # ─── purchase & verify ──────────────────────────────────────────────────────────
    #
    @action(detail=True, methods=["post"], url_path="purchase", permission_classes=[permissions.IsAuthenticated])
    def purchase(self, request, pk=None):
        course = self.get_object()
        # Free course shortcut
        if course.is_free or course.price == 0:
            Enrollment.objects.get_or_create(student=request.user, course=course)
            return Response({"detail": "Enrolled in free course."})

        # Create Order
        order = Order.objects.create(
            student=request.user,
            course=course,
            amount=course.price
        )

        # Delegate to payment app
        auth_url, reference = initialize_transaction(
            email=request.user.email,
            amount=int(course.price * 100),
            metadata={"order_id": order.id}
        )
        order.transaction_id = reference
        order.save(update_fields=["transaction_id"])
        return Response({"authorization_url": auth_url}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="verify", permission_classes=[permissions.IsAuthenticated])
    def verify(self, request, pk=None):
        order_id = request.query_params.get("order_id")
        order = get_object_or_404(Order, pk=order_id, student=request.user)
        data = verify_transaction(reference=order.transaction_id)
        # On success enroll
        if data.get("status") == "success":
            order.status = Order.COMPLETED
            order.save(update_fields=["status"])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)
            return Response({"detail": "Payment successful, enrolled."})
        return Response({"detail": "Payment failed."}, status=status.HTTP_400_BAD_REQUEST)



