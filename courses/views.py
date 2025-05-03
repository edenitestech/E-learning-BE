import hmac, hashlib
from django.conf import settings
import requests
from rest_framework import viewsets, permissions, status
from .serializers import CourseSerializer
from .models import Category, Course, Order
from .serializers import CategorySerializer
from rest_framework.decorators import action, api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from enrollments.models import Enrollment
from rest_framework.permissions import AllowAny
# Create your views here.

class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        # Make sure user is authenticated _and_ marked as instructor
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_instructor", False)
        )

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields = ["category", "instructor"]
    search_fields    = ["title", "description"]
    ordering_fields  = ["title", "created_at"]

    def get_permissions(self):
        if self.action in ["create","update","partial_update","destroy"]:
            return [IsInstructor()]
        return [permissions.AllowAny()]
    
    @action(detail=True, methods=["post"], url_path="purchase",
            permission_classes=[permissions.IsAuthenticated])
    
    # Function to initiate purchases
    def purchase(self, request, pk=None):
        course = self.get_object()

        # for free course, just auto‐enroll
        if course.price == 0:
            Enrollment.objects.get_or_create(student=request.user, course=course)
            return Response({"detail": "Enrolled in free course."})

        # create a pending order
        order = Order.objects.create(
            student=request.user,
            course=course,
            amount=course.price
        )

        # Prepare Paystack initialize endpoint
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
            # Paystack returned an error
            order.status = Order.FAILED
            order.save()
            return Response(
                {"detail": "Payment initialization failed.", "errors": resp_data.get("message")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Return authorization_url to frontend
        auth_url = resp_data["data"]["authorization_url"]
        order.transaction_id = resp_data["data"]["reference"]
        order.save(update_fields=["transaction_id"])

        return Response({"authorization_url": auth_url})
    

@csrf_exempt  
@api_view(["POST"])
@permission_classes([AllowAny])
def paystack_webhook(request):
    # Validate Paystack signature
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

        # Mark order completed & enroll student
        order.status = Order.COMPLETED
        order.save(update_fields=["status"])
        Enrollment.objects.get_or_create(student=order.student, course=order.course)

    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def verify_payment(request, order_id):
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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]