# payment/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .paystack import initialize_transaction, verify_transaction, validate_webhook_signature
from courses.models import Order
from enrollments.models import Enrollment


class InitializePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        email    = request.data.get("email", request.user.email)
        amount   = request.data["amount"]
        metadata = request.data.get("metadata", {})
        auth_url, ref = initialize_transaction(email=email, amount=amount, metadata=metadata)
        return Response({"authorization_url": auth_url, "reference": ref}, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, reference):
        data     = verify_transaction(reference=reference)
        order_id = data.get("metadata", {}).get("order_id")
        if order_id:
            order = get_object_or_404(Order, pk=order_id)
            order.status = Order.COMPLETED
            order.save(update_fields=["status"])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)
        return Response(data)


class WebhookPaymentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        validate_webhook_signature(request)
        evt = request.data
        if evt.get("event")=="charge.success":
            data = evt["data"]
            ref  = data.get("reference")
            order= Order.objects.filter(transaction_id=ref).first()
            if order:
                order.status = Order.COMPLETED
                order.save(update_fields=["status"])
                Enrollment.objects.get_or_create(student=order.student, course=order.course)
        return Response(status=status.HTTP_200_OK)
