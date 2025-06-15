# exams/urls.py
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, PastQuestionViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet)
router.register(r"past-questions", PastQuestionViewSet)
router.register(r"subscriptions", SubscriptionViewSet) 

urlpatterns = router.urls


