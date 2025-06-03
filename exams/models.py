from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class PastQuestion(models.Model):
    JAMB = "JAMB"
    WAEC = "WAEC"
    NECO = "NECO"
    JSCE = "JSCE"
    FSLC = "FSLC"
    EXAM_CHOICES = [
        (JAMB, "JAMB"),
        (WAEC, "WAEC"),
        (NECO, "NECO"),
        (JSCE, "Junior WAEC/JSCE"),
        (FSLC, "FSLC"),
    ]

    exam_type = models.CharField(max_length=20, choices=EXAM_CHOICES)
    year = models.PositiveSmallIntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="past_questions")
    question_text = models.TextField()
    solution_text = models.TextField(blank=True)
    allow_multiple = models.BooleanField(default=False, help_text="More than one option may be correct")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam_type", "year", "subject", "question_text")

    def __str__(self):
        return f"{self.exam_type} {self.year} – {self.subject.name}"


class Option(models.Model):
    question = models.ForeignKey(PastQuestion, related_name="options", on_delete=models.CASCADE)
    label = models.CharField(max_length=1, choices=[(c, c) for c in "ABCDE"], null=True)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.label}. {self.text}"
