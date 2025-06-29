# courses/urls.py
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, CourseViewSet

router = SimpleRouter(trailing_slash=True)
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"", CourseViewSet, basename="course")

urlpatterns = router.urls



