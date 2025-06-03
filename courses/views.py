import hmac
import hashlib
import requests

from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, status, filters
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
    queryset         = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields   = ["name"]


#
# ─── CourseViewSet ──────────────────────────────────────────────────────────────────
#
class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD for Courses, plus nested Lessons & Quizzes & exam‐project endpoints,
    and a `purchase` action for Paystack integration.
    """
    queryset         = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__name", "instructor__username"]
    search_fields    = ["title", "description"]
    ordering_fields  = ["title", "created_at"]

    def get_permissions(self):
        # Only instructors can create/update/delete courses
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Automatically set instructor = request.user
        serializer.save(instructor=self.request.user)

    #
    # ─── Nested: list Lessons for a Course ─────────────────────────────────────────
    #
    @action(detail=True, methods=["get"], url_path="lessons", permission_classes=[permissions.AllowAny])
    def lessons(self, request, pk=None):
        """
        GET /api/courses/{pk}/lessons/
        Returns all lessons (with nested follow‐up questions) for this course.
        If course.is_free=False and user is anonymous, only free lessons are shown.
        """
        course = self.get_object()
        lessons_qs = course.lessons.all().order_by("order")
        if not course.is_free and not request.user.is_authenticated:
            lessons_qs = lessons_qs.filter(is_free=True)

        serializer = LessonSerializer(lessons_qs, many=True, context={"request": request})
        return Response(serializer.data)

    #
    # ─── Nested: create a Lesson for this Course ───────────────────────────────────
    #
    @action(detail=True, methods=["post"], url_path="lessons", permission_classes=[IsInstructor])
    def create_lesson(self, request, pk=None):
        """
        POST /api/courses/{pk}/lessons/
        Payload must include:
        {
          "order": 1,
          "title": "Lesson Title",
          "content": "...",
          "video": <file>,
          "is_free": false,
          "followup_questions": [
            {
              "question_text": "...",
              "allow_multiple": false,
              "options": [
                {"label": "A", "text": "Choice A", "is_correct": false},
                {"label": "B", "text": "Choice B", "is_correct": true},
                …
              ]
            },
            …
          ]
        }
        """
        course = self.get_object()
        data = request.data.copy()
        data["course"] = course.id
        serializer = LessonSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #
    # ─── Nested: update/delete a Lesson by ID ───────────────────────────────────────
    #
    @action(detail=True, methods=["put", "patch", "delete"], url_path="lessons/(?P<lesson_id>[^/.]+)", permission_classes=[IsInstructor])
    def modify_lesson(self, request, pk=None, lesson_id=None):
        """
        PUT /api/courses/{pk}/lessons/{lesson_id}/
        PATCH /api/courses/{pk}/lessons/{lesson_id}/
        DELETE /api/courses/{pk}/lessons/{lesson_id}/
        """
        course = self.get_object()
        lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)

        if request.method in ["PUT", "PATCH"]:
            serializer = LessonSerializer(
                lesson,
                data=request.data,
                partial=(request.method == "PATCH"),
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # DELETE
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    #
    # ─── Nested: list Quizzes for this Course ───────────────────────────────────────
    #
    @action(detail=True, methods=["get"], url_path="quizzes", permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def list_quizzes(self, request, pk=None):
        """
        GET /api/courses/{pk}/quizzes/
        Returns both quizzes (MID1, MID2) for this course, including nested questions/options.
        """
        course = self.get_object()
        quizzes_qs = course.quizzes.all().order_by("title")
        serializer = QuizSerializer(quizzes_qs, many=True, context={"request": request})
        return Response(serializer.data)

    #
    # ─── Nested: create a Quiz for this Course ──────────────────────────────────────
    #
    @action(detail=True, methods=["post"], url_path="quizzes", permission_classes=[IsInstructor])
    def create_quiz(self, request, pk=None):
        """
        POST /api/courses/{pk}/quizzes/
        Payload:
        {
          "title": "MID1",
          "questions": [
            {
              "question_text": "...",
              "allow_multiple": false,
              "options": [
                {"label":"A","text":"...","is_correct":false},
                {"label":"B","text":"...","is_correct":true},
                …
              ]
            },
            …
          ]
        }
        """
        course = self.get_object()
        data = request.data.copy()
        data["course"] = course.id
        serializer = QuizSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #
    # ─── Nested: update/delete a Quiz by ID ─────────────────────────────────────────
    #
    @action(detail=True, methods=["put", "patch", "delete"], url_path="quizzes/(?P<quiz_id>[^/.]+)", permission_classes=[IsInstructor])
    def modify_quiz(self, request, pk=None, quiz_id=None):
        """
        PUT /api/courses/{pk}/quizzes/{quiz_id}/
        PATCH /api/courses/{pk}/quizzes/{quiz_id}/
        DELETE /api/courses/{pk}/quizzes/{quiz_id}/
        """
        course = self.get_object()
        quiz = get_object_or_404(Quiz, pk=quiz_id, course=course)

        if request.method in ["PUT", "PATCH"]:
            serializer = QuizSerializer(
                quiz,
                data=request.data,
                partial=(request.method == "PATCH"),
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # DELETE
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    #
    # ─── Nested: submit final exam/project ──────────────────────────────────────────
    #
    @action(detail=True, methods=["post"], url_path="exam-project", permission_classes=[permissions.IsAuthenticated])
    def submit_exam(self, request, pk=None):
        """
        POST /api/courses/{pk}/exam-project/
        Payload: { "submission_file": <file> }
        """
        course = self.get_object()
        data = {
            "course": course.id,
            "submission_file": request.data.get("submission_file"),
        }
        serializer = ExamProjectSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(student=request.user, course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #
    # ─── Instructor: approve a student’s exam/project submission ────────────────────
    #
    @action(detail=True, methods=["post"], url_path="exam-project/(?P<submission_id>[^/.]+)/approve", permission_classes=[IsInstructor])
    def approve_exam(self, request, pk=None, submission_id=None):
        """
        POST /api/courses/{pk}/exam-project/{submission_id}/approve/
        Payload: { "score": 55.0, "certificate_file": <file> }
        """
        course = self.get_object()
        submission = get_object_or_404(ExamProject, pk=submission_id, course=course)
        if submission.is_approved:
            return Response({"detail": "Already approved."}, status=status.HTTP_400_BAD_REQUEST)

        score     = request.data.get("score")
        cert_file = request.FILES.get("certificate_file")
        if score is None or cert_file is None:
            return Response(
                {"detail": "Must provide both score and certificate_file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        submission.score            = score
        submission.certificate_file = cert_file
        submission.is_approved      = True
        submission.save()

        return Response(
            ExamProjectSerializer(submission, context={"request": request}).data
        )

    #
    # ─── purchase action (Paystack integration) ─────────────────────────────────────
    #
    @action(
        detail=True,
        methods=["post"],
        url_path="purchase",
        permission_classes=[permissions.IsAuthenticated],
    )
    def purchase(self, request, pk=None):
        """
        POST /api/courses/{pk}/purchase/
        If course.is_free=True or price==0 → auto-enroll.
        Otherwise → create an Order & return Paystack auth URL.
        """
        course = self.get_object()

        # Free course: auto-enroll
        if course.is_free or course.price == 0:
            Enrollment.objects.get_or_create(student=request.user, course=course)
            return Response({"detail": "Enrolled in free course."})

        # Otherwise: create an Order and initialize Paystack
        order = Order.objects.create(
            student=request.user,
            course=course,
            amount=course.price
        )

        initialize_url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": request.user.email,
            "amount": int(course.price * 100),  # in kobo
            "metadata": {"order_id": order.id},
            "callback_url": f"{settings.DOMAIN}/api/payments/verify/{order.id}/"
        }

        resp = requests.post(initialize_url, json=data, headers=headers)
        resp_data = resp.json()

        if not resp_data.get("status"):
            order.status = Order.FAILED
            order.save(update_fields=["status"])
            return Response(
                {
                    "detail": "Payment initialization failed.",
                    "errors": resp_data.get("message", "Unknown error"),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        auth_url                 = resp_data["data"]["authorization_url"]
        order.transaction_id      = resp_data["data"]["reference"]
        order.save(update_fields=["transaction_id"])
        return Response({"authorization_url": auth_url}, status=status.HTTP_201_CREATED)


#
# ─── Order & Payment Endpoints (exposed under /api/payments/) ────────────────────
#
class PaymentsViewSet(viewsets.ViewSet):
    """
    Exposes:
    - POST /api/payments/purchase/{course_id}/
    - POST /api/payments/webhook/
    - GET  /api/payments/verify/{order_id}/
    """
    permission_classes = [permissions.AllowAny]

    @action(
        detail=False,
        methods=["post"],
        url_path="purchase/(?P<course_id>[^/.]+)",
        permission_classes=[permissions.IsAuthenticated],
    )
    def purchase(self, request, course_id=None):
        """
        Proxy to CourseViewSet.purchase
        """
        cv = CourseViewSet.as_view({"post": "purchase"})
        return cv(request, pk=course_id)

    @action(
        detail=False,
        methods=["post"],
        url_path="webhook",
        permission_classes=[permissions.AllowAny],
    )
    def webhook(self, request):
        """
        POST /api/payments/webhook/
        Validate signature; if successful → mark Order completed & enroll.
        """
        signature    = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")
        computed_sig = hmac.new(
            settings.PAYSTACK_WEBHOOK_SECRET.encode(),
            msg=request.body,
            digestmod=hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(computed_sig, signature):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event = request.data
        if event.get("event") == "charge.success":
            data = event["data"]
            ref  = data["reference"]
            try:
                order = Order.objects.get(transaction_id=ref)
            except Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            order.status = Order.COMPLETED
            order.save(update_fields=["status"])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)

        return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="verify/(?P<order_id>[^/.]+)",
        permission_classes=[permissions.IsAuthenticated],
    )
    def verify(self, request, order_id=None):
        """
        GET /api/payments/verify/{order_id}/
        Check Paystack; if successful → mark Order completed & enroll.
        """
        try:
            order = Order.objects.get(id=order_id, student=request.user)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        verify_url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{order.transaction_id}"
        headers    = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        resp       = requests.get(verify_url, headers=headers).json()

        if resp.get("data", {}).get("status") == "success":
            order.status = Order.COMPLETED
            order.save(update_fields=["status"])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)
            return Response({"detail": "Payment successful, enrolled."})

        return Response({"detail": "Payment not successful."}, status=status.HTTP_400_BAD_REQUEST)
