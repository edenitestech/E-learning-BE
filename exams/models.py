from django.db import models

# Create your models here.

class PastQuestion(models.Model):
    JAMB = "JAMB"
    WAEC = "WAEC"
    EXAM_CHOICES = [(JAMB, "JAMB"), (WAEC, "WAEC")]

    exam_type      = models.CharField(max_length=4, choices=EXAM_CHOICES)
    year           = models.PositiveSmallIntegerField()
    subject        = models.CharField(max_length=100)
    question_text  = models.TextField()
    solution_text  = models.TextField()
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam_type", "year", "subject")
