# courses/urls.py
# ─── Router & URLs ────────────────────────────────────────────────────────────────
#
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CourseViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"courses",    CourseViewSet)

urlpatterns = router.urls


