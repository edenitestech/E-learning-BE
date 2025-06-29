# courses/views.py

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Course, Lesson, Quiz, Order
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LessonSerializer,
    QuizSerializer,
)
from enrollments.models import Enrollment
from payment.paystack import initialize_transaction, verify_transaction


class IsInstructor(permissions.BasePermission):
    """
    Only allow access if user.is_authenticated AND user.is_instructor=True.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_instructor", False)
        )

class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for Course Categories.
    GET/HEAD/OPTIONS: public
    POST/PUT/PATCH/DELETE: authenticated
    """
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD for Courses + unified lessons/quizzes actions + purchase/verify.
    """
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__name", "instructor__username"]
    search_fields    = ["title", "description"]
    ordering_fields  = ["title", "created_at"]

    def get_permissions(self):
        # Public: list & retrieve courses
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        # Public GET lessons/quizzes
        if self.action in ["lessons", "quizzes"] and self.request.method == "GET":
            return [permissions.AllowAny()]

        # Instructor-only POST lessons/quizzes
        if self.action in ["lessons", "quizzes"] and self.request.method == "POST":
            return [IsInstructor()]

        # Instructor-only: create/update/delete courses
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor()]

        # Authenticated for purchase & verify
        if self.action in ["purchase", "verify"]:
            return [permissions.IsAuthenticated()]

        # Fallback deny
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    #
    # ─── Unified Lessons endpoint ─────────────────────────────────────────
    #
    # ─── unified lessons endpoint for LIST, CREATE, RETRIEVE, UPDATE, DELETE ───
    @action(
        detail=True,
        methods=["get", "post", "put", "patch", "delete"],
        url_path=r"lessons(?:/(?P<lesson_id>[^/.]+))?"
    )
    def lessons(self, request, pk=None, lesson_id=None):
        """
        • GET    /api/courses/{pk}/lessons/           → list lessons  
        • POST   /api/courses/{pk}/lessons/           → create lesson  
        • GET    /api/courses/{pk}/lessons/{lesson_id}/  → retrieve  
        • PUT    /api/courses/{pk}/lessons/{lesson_id}/  → replace  
        • PATCH  /api/courses/{pk}/lessons/{lesson_id}/  → partial update  
        • DELETE /api/courses/{pk}/lessons/{lesson_id}/  → remove
        """
        course = self.get_object()

        # LIST all lessons
        if request.method == "GET" and lesson_id is None:
            qs = course.lessons.order_by("order")
            if not course.is_free and not request.user.is_authenticated:
                qs = qs.filter(is_free=True)
            return Response(LessonSerializer(qs, many=True, context={"request": request}).data)

        # RETRIEVE single lesson
        if request.method == "GET" and lesson_id is not None:
            lesson = get_object_or_404(Lesson, course=course, pk=lesson_id)
            # enforce enrollment on paid content
            if not course.is_free and not Enrollment.objects.filter(
                student=request.user, course=course
            ).exists():
                return Response({"detail":"Enroll to view."}, status=status.HTTP_403_FORBIDDEN)
            return Response(LessonSerializer(lesson, context={"request": request}).data)

        # CREATE new lesson (instructor only)
        if request.method == "POST":
            payload = {**request.data, "course": course.id}
            serializer = LessonSerializer(data=payload, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # At this point we know lesson_id must be set for PUT/PATCH/DELETE
        lesson = get_object_or_404(Lesson, course=course, pk=lesson_id)

        # UPDATE
        if request.method in ("PUT", "PATCH"):
            partial = (request.method == "PATCH")
            serializer = LessonSerializer(
                lesson, data=request.data, partial=partial, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # DELETE
        if request.method == "DELETE":
            lesson.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Should never get here
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    #
    # ─── Unified Quizzes endpoint ─────────────────────────────────────────
    #
    @action(detail=True, methods=["get", "post"], url_path="quizzes")
    def quizzes(self, request, pk=None):
        """
        GET  /api/courses/{pk}/quizzes/     → list quizzes
        POST /api/courses/{pk}/quizzes/     → create quiz
        """
        course = self.get_object()

        # LIST
        if request.method == "GET":
            qs = course.quizzes.order_by("title")
            serializer = QuizSerializer(qs, many=True, context={"request": request})
            return Response(serializer.data)

        # CREATE
        data = {**request.data, "course": course.id}
        serializer = QuizSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["put", "patch", "delete"],
        url_path=r"quizzes/(?P<quiz_id>[^/.]+)"
    )
    def modify_quiz(self, request, pk=None, quiz_id=None):
        """
        PUT/PATCH/DELETE /api/courses/{pk}/quizzes/{quiz_id}/
        """
        course = self.get_object()
        quiz = get_object_or_404(Quiz, course=course, pk=quiz_id)

        if request.method in ("PUT", "PATCH"):
            partial = (request.method == "PATCH")
            serializer = QuizSerializer(
                quiz,
                data=request.data,
                partial=partial,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # DELETE
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #
    # ─── Purchase & Verify ─────────────────────────────────────────────
    #
    @action(detail=True, methods=["post"], url_path="purchase")
    def purchase(self, request, pk=None):
        """
        POST /api/courses/{pk}/purchase/
        """
        course = self.get_object()
        if course.is_free or course.price == 0:
            Enrollment.objects.get_or_create(student=request.user, course=course)
            return Response({"detail": "Enrolled in free course."})

        order = Order.objects.create(
            student=request.user,
            course=course,
            amount=course.price
        )
        auth_url, reference = initialize_transaction(
            email=request.user.email,
            amount=int(course.price * 100),
            metadata={"order_id": order.id},
        )
        order.transaction_id = reference
        order.save(update_fields=["transaction_id"])
        return Response({"authorization_url": auth_url}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="verify")
    def verify(self, request, pk=None):
        """
        GET /api/courses/{pk}/verify/?order_id={order_id}
        """
        order_id = request.query_params.get("order_id")
        order = get_object_or_404(Order, pk=order_id, student=request.user)
        data = verify_transaction(reference=order.transaction_id)
        if data.get("status") == "success":
            order.status = Order.COMPLETED
            order.save(update_fields=["status"])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)
            return Response({"detail": "Payment successful, enrolled."})
        return Response({"detail": "Payment failed."}, status=status.HTTP_400_BAD_REQUEST)
