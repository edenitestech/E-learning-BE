from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, QuestionViewSet

router = DefaultRouter()
router.register(r"lessons",    LessonViewSet,   basename="lesson")
router.register(r"questions",  QuestionViewSet, basename="question")

urlpatterns = router.urls
