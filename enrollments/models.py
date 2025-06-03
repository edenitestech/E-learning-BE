from django.db import models
from django.conf import settings
from content.models import Lesson, Question

class Enrollment(models.Model):
    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course      = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson     = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed  = models.BooleanField(default=False)

    def __str__(self):
        status = "✔" if self.completed else "❌"
        return f"{self.enrollment.student.username} – {self.lesson.title} [{status}]"


class Answer(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE)
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    selected   = models.CharField(max_length=1)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.student.username} answered Q#{self.question.id} → {self.selected} ({'✓' if self.is_correct else '✗'})"
