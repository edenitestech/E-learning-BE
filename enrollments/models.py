# enrollments/models.py
from django.db import models
from django.conf import settings
from courses.models import Lesson, FollowUpQuestion  # <- Ensure you import from courses now.

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

class Answer(models.Model):
    # The `question` now refers to FollowUpQuestion (formerly content.Question)
    question = models.ForeignKey(FollowUpQuestion, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    selected = models.CharField(max_length=1)  # e.g. "A", "B", "C", "D"
    is_correct = models.BooleanField()
