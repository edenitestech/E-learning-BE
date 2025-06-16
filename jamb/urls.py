# jamb/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import JAMBSubjectViewSet, JAMBQuestionViewSet, StrategyViewSet

router = DefaultRouter()
router.register(r"subjects",   JAMBSubjectViewSet,  basename="jamb-subject")
router.register(r"questions",  JAMBQuestionViewSet, basename="jamb-question")
router.register(r"strategies", StrategyViewSet,     basename="jamb-strategy")

urlpatterns = router.urls
