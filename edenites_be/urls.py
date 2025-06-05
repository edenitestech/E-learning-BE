# edenites_be/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from courses.views     import CategoryViewSet, CourseViewSet, PaymentsViewSet
from enrollments.views import EnrollmentViewSet
from exams.views       import PastQuestionViewSet
from .api_overview import api_plaintext_overview

# Import the new viewsets for JAMB and testimonials
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
# Existing registrations
router.register(r"categories", CategoryViewSet)
router.register(r"courses",    CourseViewSet)
router.register(r"payments",   PaymentsViewSet, basename="payments")
# router.register(r"lessons",    LessonViewSet)
# router.register(r"questions",  QuestionViewSet)
router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")
router.register(r"exams/past-questions", PastQuestionViewSet, basename="pastquestion")

# New registrations for JAMB
router.register(r"jamb/subjects",   JAMBSubjectViewSet,  basename="jamb-subject")
router.register(r"jamb/questions",  JAMBQuestionViewSet, basename="jamb-question")
router.register(r"jamb/strategies", StrategyViewSet,     basename="jamb-strategy")

# New registration for testimonials
router.register(r"testimonials", TestimonialViewSet, basename="testimonial")


urlpatterns = [
    # Redirect root to the API root
    path("", RedirectView.as_view(url="/api/", permanent=False)),

    # Admin
    path("admin/", admin.site.urls),

    # API root (all ViewSets)
    path("api/", include(router.urls)),

    # Auth endpoints (login, register, GDPR, etc.)
    path("api/auth/",        include("accounts.urls")),
    path("api/courses/",     include("courses.urls")),
    # path("api/content/",     include("content.urls")),
    path("api/enrollments/", include("enrollments.urls")),
    path("api/overview/", api_plaintext_overview, name="api_plaintext_overview"),
    

    # Note: we no longer include 'jamb.urls' or 'testimonials.urls' here,
    # because their routes have been registered directly on the router above.
]

# Serve media files in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
