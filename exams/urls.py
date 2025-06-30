# exams/urls.py


from rest_framework.routers import DefaultRouter
from .views import ExamSubjectViewSet, PastQuestionViewSet, SubscriptionViewSet

router = DefaultRouter()
# GET /api/exams/subjects/       POST /api/exams/subjects/
# GET /api/exams/subjects/{pk}/  etc.
router.register(r"subjects", ExamSubjectViewSet, basename="exam-subject")

# GET /api/exams/past-questions/        POST /api/exams/past-questions/
# GET /api/exams/past-questions/{pk}/   PUT/PATCH/DELETE /api/exams/past-questions/{pk}/
# + extra actions: /quiz/, /practice/, /subjects/
router.register(r"past-questions", PastQuestionViewSet, basename="past-question")

# GET /api/exams/subscriptions/
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = router.urls
