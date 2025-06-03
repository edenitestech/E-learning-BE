from rest_framework.routers import DefaultRouter
from .views import PastQuestionViewSet, SubjectViewSet

router = DefaultRouter()
router.register(r"past-questions", PastQuestionViewSet, basename="pastquestion")
router.register(r"subjects", SubjectViewSet, basename="subject")

urlpatterns = router.urls
