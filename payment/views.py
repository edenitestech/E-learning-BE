from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django.shortcuts import get_object_or_404
from django.conf import settings

from .paystack import initialize_transaction, verify_transaction, validate_webhook_signature
from courses.models import Order
from enrollments.models import Enrollment

class InitializePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        POST /api/payments/initialize/
        { "email": "", "amount": 50000, "metadata": { "order_id": 1 } }
        """
        email    = request.data.get('email') or request.user.email
        amount   = request.data.get('amount')
        metadata = request.data.get('metadata', {})
        auth_url, reference = initialize_transaction(email=email, amount=amount, metadata=metadata)
        return Response({'authorization_url': auth_url, 'reference': reference}, status=status.HTTP_201_CREATED)

class VerifyPaymentView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, reference):
        """
        GET /api/payments/verify/{reference}/
        """
        data = verify_transaction(reference=reference)
        # If metadata contains order_id, update that order
        order_id = data.get('metadata', {}).get('order_id')
        if order_id:
            order = get_object_or_404(Order, pk=order_id)
            order.status = Order.COMPLETED
            order.save(update_fields=['status'])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)
        return Response(data, status=status.HTTP_200_OK)

class WebhookPaymentView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        POST /api/payments/webhook/
        """
        # Validate signature
        validate_webhook_signature(request)

        event = request.data
        if event.get('event') == 'charge.success':
            data = event.get('data', {})
            ref  = data.get('reference')
            # Look up order by reference
            try:
                order = Order.objects.get(transaction_id=ref)
            except Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            order.status = Order.COMPLETED
            order.save(update_fields=['status'])
            Enrollment.objects.get_or_create(student=order.student, course=order.course)

        return Response(status=status.HTTP_200_OK)
