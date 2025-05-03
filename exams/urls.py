# exams/urls.py

from rest_framework.routers import DefaultRouter
from .views import PastQuestionViewSet

router = DefaultRouter()
router.register(r"past-questions", PastQuestionViewSet, basename="pastquestion")
urlpatterns = router.urls
