from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, QuestionViewSet, OptionViewSet

router = DefaultRouter()
router.register(r"lessons", LessonViewSet,       basename="lesson")
router.register(r"questions", QuestionViewSet,   basename="question")
router.register(r"options",   OptionViewSet,     basename="option")

urlpatterns = router.urls
