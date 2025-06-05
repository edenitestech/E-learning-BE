import os
from decimal import Decimal

from django.conf import settings
from django.db import models


def certificate_upload_path(instance, filename):
    # Upload certificates under: certificates/{course_id}/{student_id}/{filename}
    return os.path.join(
        "certificates",
        f"course_{instance.course.id}",
        f"student_{instance.student.id}",
        filename,
    )


class Category(models.Model):
    """
    A category/tag for grouping multiple courses.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Core course model.
    """
    title       = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    instructor  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructed_courses"
    )
    price       = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    is_free     = models.BooleanField(
        default=False,
        help_text="If True, course is entirely free; otherwise price applies."
    )
    created_at  = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """
    A single lesson inside a Course.
    """
    course      = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title       = models.CharField(max_length=200)
    content     = models.TextField(help_text="Lesson content/description.")
    video       = models.FileField(upload_to="lesson_videos/", blank=True, null=True)
    is_free     = models.BooleanField(default=False, help_text="If True, this lesson is free preview.")
    order       = models.PositiveIntegerField(default=1, help_text="Display order within the course.")
    created_at  = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ("course", "order")
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} ► Lesson {self.order}: {self.title}"


class FollowUpQuestion(models.Model):
    """
    A multiple-choice question tied to a single Lesson. Now includes 'solution_text.'
    """
    lesson          = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="followup_questions"
    )
    question_text   = models.TextField()
    solution_text   = models.TextField(null=True, help_text="Official solution/explanation.")
    allow_multiple  = models.BooleanField(
        default=False,
        help_text="If True, more than one choice may be marked correct."
    )

    def __str__(self):
        # show first 40 chars of question_text
        return f"Q: {self.question_text[:40]}… (Lesson: {self.lesson.title})"


class FollowUpOption(models.Model):
    """
    One choice for a FollowUpQuestion.
    """
    LABEL_CHOICES = [(c, c) for c in "ABCD"]

    question   = models.ForeignKey(
        FollowUpQuestion,
        on_delete=models.CASCADE,
        related_name="options"
    )
    label      = models.CharField(max_length=1, choices=LABEL_CHOICES)
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("question", "label")
        ordering = ["label"]

    def __str__(self):
        return f"{self.label}. {self.text}"


class Quiz(models.Model):
    """
    Represents an in‐course quiz. We create exactly two per Course:
    - MID1 (out of 20)
    - MID2 (out of 20)
    """
    MID1 = "MID1"
    MID2 = "MID2"
    QUIZ_CHOICES = [
        (MID1, "Mid‐Course Quiz 1"),
        (MID2, "Mid‐Course Quiz 2"),
    ]
    course     = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title      = models.CharField(max_length=20, choices=QUIZ_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ("course", "title")

    def __str__(self):
        return f"{self.course.title} ► {self.get_title_display()}"


class QuizQuestion(models.Model):
    """
    A multiple‐choice question inside a Quiz.
    """
    quiz           = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    question_text  = models.TextField()
    solution_text  = models.TextField(null=True, help_text="Official solution/explanation.")
    allow_multiple = models.BooleanField(default=False)

    def __str__(self):
        return f"Quiz {self.quiz.title}: {self.question_text[:40]}…"


class QuizOption(models.Model):
    """
    One choice for a QuizQuestion.
    """
    LABEL_CHOICES = [(c, c) for c in "ABCD"]

    question   = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name="options"
    )
    label      = models.CharField(max_length=1, choices=LABEL_CHOICES)
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("question", "label")
        ordering = ["label"]

    def __str__(self):
        return f"{self.question.quiz.course.title} ► {self.question.quiz.title} ► {self.label}. {self.text}"


class ExamProject(models.Model):
    """
    Final exam or project submission by a student.
    Scored out of 60. Once approved by instructor/admin, student can download a certificate.
    """
    course           = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="exam_projects"
    )
    student          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_submissions"
    )
    submission_file  = models.FileField(upload_to="exam_submissions/")
    submitted_at     = models.DateTimeField(auto_now_add=True)
    score            = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_approved      = models.BooleanField(default=False)
    certificate_file = models.FileField(
        upload_to=certificate_upload_path,
        blank=True,
        null=True,
        help_text="Generated certificate (PDF/image) once approved."
    )

    class Meta:
        unique_together = ("course", "student")

    def __str__(self):
        return f"{self.student.username} – {self.course.title} ExamProject"


class Order(models.Model):
    """
    Tracks a student’s attempt to purchase a paid course.
    """
    PENDING   = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED    = "FAILED"
    STATUS_CHOICES = [
        (PENDING,   "Pending"),
        (COMPLETED, "Completed"),
        (FAILED,    "Failed"),
    ]

    student        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    course         = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    amount         = models.DecimalField(max_digits=8, decimal_places=2)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at     = models.DateTimeField(auto_now_add=True, null=True)
    updated_at     = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} – {self.student.username} ⇒ {self.course.title} [{self.status}]"
