from django.db import models
from courses.models import Course

class Lesson(models.Model):
    course     = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="content_lessons"
    )
    title      = models.CharField(max_length=200)
    video      = models.FileField(upload_to="videos/")
    is_free    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    lesson         = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text           = models.TextField()
    allow_multiple = models.BooleanField(
        default=False,
        help_text="If true, more than one option may be marked correct"
    )
    explanation    = models.TextField()
    created_at     = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        # Show a snippet of the question text
        return f"{self.lesson.title} – {self.text[:30]}…"


class Option(models.Model):
    QUESTION_LABEL_CHOICES = [(chr(i), chr(i)) for i in range(65, 91)]  # “A” through “Z”
    question   = models.ForeignKey(
        Question,
        related_name="options",
        on_delete=models.CASCADE
    )
    label      = models.CharField(
        max_length=1,
        choices=QUESTION_LABEL_CHOICES,
        help_text="Choose exactly one letter (A, B, C, …) per option"
    )
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(
        default=False,
        help_text="Mark True if this option is correct for the question"
    )

    class Meta:
        unique_together = (("question", "label"),)

    def __str__(self):
        return f"{self.label}. {self.text}"
