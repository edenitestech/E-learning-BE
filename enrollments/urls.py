from rest_framework.routers import DefaultRouter
from .views import EnrollmentViewSet, LessonProgressViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r"enrollments",    EnrollmentViewSet,       basename="enrollment")
router.register(r"progress",       LessonProgressViewSet,  basename="progress")
router.register(r"answers",        AnswerViewSet,           basename="answer")

urlpatterns = router.urls
