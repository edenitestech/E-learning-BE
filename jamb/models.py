# jamb/models.py

from django.db import models

class JAMBSubject(models.Model):
    """
    One JAMB subject (e.g. English, Mathematics, etc.).
    """
    name     = models.CharField(max_length=100, unique=True)
    slug     = models.SlugField(max_length=100, unique=True)
    topics   = models.PositiveIntegerField(default=0)      # e.g. 30
    duration = models.CharField(max_length=50, blank=True) # e.g. "45 hours"

    def __str__(self):
        return self.name


class JAMBQuestion(models.Model):
    """
    A single practice question, tied to one JAMBSubject.
    `options` stored as a JSON list: e.g. ["5", "7", "12", "25"]
    `correct_index` is an integer 0..3.
    """
    subject        = models.ForeignKey(
        JAMBSubject,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    question_text  = models.TextField()
    options        = models.JSONField()             # list of strings
    correct_index  = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.subject.slug} Q#{self.id}"


class Strategy(models.Model):
    """
    Exam strategy tips (e.g. Time Management Tips, Answering Techniques, etc.).
    """
    category = models.CharField(max_length=100)   # e.g. "Time Management Tips"
    content  = models.TextField()                 # long text with bullet points or paragraphs

    def __str__(self):
        return self.category
