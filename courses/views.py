# courses/views.py

import hmac
import hashlib
import requests

from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Course, Order
from .serializers import CategorySerializer, CourseSerializer, OrderSerializer
from enrollments.models import Enrollment

class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_instructor", False)
        )

class CourseViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for courses, plus per-course `purchase` action.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields  = ["category", "instructor"]
    search_fields     = ["title", "description"]
    ordering_fields   = ["title", "created_at"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor()]
        return [permissions.AllowAny()]

    @action(
        detail=True,
        methods=["post"],
        url_path="purchase",
        permission_classes=[permissions.IsAuthenticated],
    )
    def purchase(self, request, pk=None):
        course = self.get_object()

        # Free course: auto-enroll
        if course.price == 0:
            Enrollment.objects.get_or_create(student=request.user, course=course)
            return Response({"detail": "Enrolled in free course."})

        # Create pending Order
        order = Order.objects.create(
            student=request.user,
            course=course,
            amount=course.price
        )

        # Initialize Paystack transaction
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
                {"detail": "Payment initialization failed.", "errors": resp_data.get("message")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Return Paystack authorization URL
        auth_url = resp_data["data"]["authorization_url"]
        order.transaction_id = resp_data["data"]["reference"]
        order.save(update_fields=["transaction_id"])

        return Response({"authorization_url": auth_url}, status=status.HTTP_201_CREATED)


class PaymentsViewSet(viewsets.ViewSet):
    """
    Exposes purchase, webhook, and verify under /api/payments/
    so they appear in the API root.
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
        Alternative route for initiating purchase:
        POST /api/payments/purchase/{course_id}/
        """
        # Delegate to CourseViewSet.purchase for DRYness:
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
        Handles Paystack webhook:
        POST /api/payments/webhook/
        """
        signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")
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
        Verifies payment status:
        GET /api/payments/verify/{order_id}/
        """
        try:
            order = Order.objects.get(id=order_id, student=request.user)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        verify_url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{order.transaction_id}"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        resp = requests.get(verify_url, headers=headers).json()

        if resp.get("data", {}).get("status") == "success":
            order.status = Order.COMPLETED
            order.save(update_fields=["status"])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)
            return Response({"detail": "Payment successful, enrolled."})

        return Response({"detail": "Payment not successful."}, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for course categories.
    """
    queryset         = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
