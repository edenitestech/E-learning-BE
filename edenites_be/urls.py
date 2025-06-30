# edenites_be/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from courses.views     import CategoryViewSet, CourseViewSet
from enrollments.views import EnrollmentViewSet
from exams.views       import PastQuestionViewSet
from .api_overview     import api_plaintext_overview

from jamb.views         import JAMBSubjectViewSet, JAMBQuestionViewSet, StrategyViewSet
from testimonials.views import TestimonialViewSet


class PublicDefaultRouter(DefaultRouter):
    """
    Override DRF's API root to be publicly readable.
    """
    def get_api_root_view(self, api_urls=None):
        view = super().get_api_root_view(api_urls=api_urls)
        view.cls.permission_classes = [AllowAny]
        return view


router = PublicDefaultRouter()

# Core course endpoints
router.register(r"categories", CategoryViewSet)
# router.register(r"courses",    CourseViewSet,    basename="course")
# Enrollments & past-exam endpoints
router.register(r"enrollments",           EnrollmentViewSet,    basename="enrollment")
router.register(r"exams/past-questions",  PastQuestionViewSet,  basename="pastquestion")
# JAMB endpoints
router.register(r"jamb/subjects",   JAMBSubjectViewSet,  basename="jamb-subject")
router.register(r"jamb/questions",  JAMBQuestionViewSet, basename="jamb-question")
router.register(r"jamb/strategies", StrategyViewSet,     basename="jamb-strategy")
# Testimonials
router.register(r"testimonials", TestimonialViewSet, basename="testimonial")


urlpatterns = [
    # Redirect root to the API root
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    # Admin site
    path("admin/", admin.site.urls),
    # API root & all registered ViewSets
    path("api/", include(router.urls)),
    path("api/courses/", include("courses.urls")),
    # Auth endpoints (login, register, GDPR, etc.)
    path("api/auth/", include("accounts.urls")),
    # Include payment URLs for initialize, verify, webhook
    path("api/", include("payment.urls")),
    # A plain-text overview of the API
    path("api/overview/", api_plaintext_overview, name="api_plaintext_overview"),
    path("api/exams/", include("exams.urls")),
]

# Serve media files in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
