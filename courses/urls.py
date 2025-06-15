#
# ─── Router & URLs ────────────────────────────────────────────────────────────────
#
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CourseViewSet, PaymentsViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"courses",    CourseViewSet)
router.register(r"", r"courses", CourseViewSet, basename="course")
router.register(r"payments",   PaymentsViewSet, basename="payments")

urlpatterns = router.urls


