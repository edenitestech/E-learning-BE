# testimonials/views.py

from rest_framework import viewsets, permissions
from .models import Testimonial
from .serializers import TestimonialSerializer

class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/testimonials/
    GET /api/testimonials/{pk}/
    """
    queryset = Testimonial.objects.all().order_by("id")
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]
