# testimonials/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TestimonialViewSet

router = DefaultRouter()
router.register(r"", TestimonialViewSet, basename="testimonial")

urlpatterns = router.urls
