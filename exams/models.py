from django.db import models

# Create your models here.

class PastQuestion(models.Model):
    JAMB = "JAMB"
    WAEC = "WAEC"
    NECO = "NECO"
    JSCE = "Junior WAEC/JSCE"
    FSLC = "FSLC"
    EXAM_CHOICES = [
        (JAMB, "JAMB"), 
        (WAEC, "WAEC"), 
        (NECO, "NECO"),
        (JSCE, "Junior WAEC/JSCE"),
        (FSLC, "FSLC"),
        ]

    exam_type      = models.CharField(max_length=20, choices=EXAM_CHOICES)
    year           = models.PositiveSmallIntegerField()
    subject        = models.CharField(max_length=100)
    question_text  = models.TextField()
    solution_text  = models.TextField()
    created_at     = models.DateTimeField(auto_now_add=True)
    allow_multiple = models.BooleanField(
        default=False,
        help_text="If true, more than one option may be correct"
    )
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam_type", "year", "subject", "question_text")

    def __str__(self):
        return f"{self.exam_type} {self.year} – {self.subject}"

    class Meta:
        unique_together = ("exam_type", "year", "subject")


class Option(models.Model):
    """
    A single answer choice for a PastQuestion.
    """
    question  = models.ForeignKey(
        PastQuestion,
        related_name="options",
        on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(
        default=False,
        help_text="Mark True for correct answers"
    )

    def __str__(self):
        return self.text