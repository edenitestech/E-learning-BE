from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ExamSubject(models.Model):
    """
    A “subject” (e.g. English Language, Mathematics, etc.) for PastQuestions.
    Similar in spirit to JAMBSubject, but scoped to this exams app.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Auto‐slugify from name if not provided
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PastQuestion(models.Model):
    """
    A single past question (e.g. JAMB 2024, Mathematics).
    The subject is a ForeignKey to ExamSubject.
    """
    JAMB = "JAMB"
    WAEC = "WAEC"
    NECO = "NECO"
    JSCE = "JSCE"  # Junior WAEC/JSCE
    FSLC = "FSLC"
    EXAM_CHOICES = [
        (JAMB, "JAMB"),
        (WAEC, "WAEC"),
        (NECO, "NECO"),
        (JSCE, "Junior WAEC/JSCE"),
        (FSLC, "FSLC"),
    ]

    exam_type       = models.CharField(max_length=10, choices=EXAM_CHOICES)
    year            = models.PositiveSmallIntegerField()
    subject         = models.ForeignKey(
        ExamSubject,
        on_delete=models.CASCADE,
        related_name="past_questions"
    )
    question_text   = models.TextField()
    solution_text   = models.TextField(help_text="Official solution/explanation.")
    allow_multiple  = models.BooleanField(
        default=False,
        help_text="If True, more than one choice may be correct."
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure no duplicates for the same exam_type/year/subject/question_text
        unique_together = ("exam_type", "year", "subject", "question_text")
        ordering = ["-year"]

    def __str__(self):
        return f"{self.exam_type} {self.year} – {self.subject.slug} (Q#{self.id})"


class PastOption(models.Model):
    """
    A single choice (A–D) for a PastQuestion.
    """
    LABEL_CHOICES = [(c, c) for c in "ABCD"]

    question   = models.ForeignKey(
        PastQuestion,
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
        return f"{self.question.exam_type} {self.question.year} [{self.label}] {self.text}"

# class ExamSubscription(models.Model):
#     """
#     Tracks a user’s subscription to a given exam_type.  We create one row
#     per (user, exam_type) when they attempt to subscribe.  Once payment succeeds,
#     status → COMPLETED, which unlocks all PastQuestions of that exam_type.
#     """
#     PENDING   = "PENDING"
#     COMPLETED = "COMPLETED"
#     FAILED    = "FAILED"

#     STATUS_CHOICES = [
#         (PENDING,   "Pending"),
#         (COMPLETED, "Completed"),
#         (FAILED,    "Failed"),
#     ]

#     user           = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="exam_subscriptions"
#     )
#     exam_type      = models.CharField(max_length=20, choices=PastQuestion.EXAM_CHOICES)
#     amount         = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=Decimal("0.00"),
#         help_text="Fee (e.g. in NGN) used to purchase this subscription."
#     )
#     status         = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default=PENDING
#     )
#     transaction_id = models.CharField(max_length=200, blank=True, null=True)
#     created_at     = models.DateTimeField(auto_now_add=True)
#     updated_at     = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ("user", "exam_type")

#     def __str__(self):
#         return f"{self.user.username} → {self.exam_type} [{self.status}]"
