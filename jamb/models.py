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

    We replaced the old JSONField('options') + 'correct_index' with
    four explicit CharFields for options A..D, and a single-letter 'correct_choice'.
    """
    CHOICE_LETTERS = [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ]

    subject       = models.ForeignKey(
        JAMBSubject,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    question_text = models.TextField()

    option_a      = models.CharField("Option A", max_length=255, null=True)
    option_b      = models.CharField("Option B", max_length=255, null=True)
    option_c      = models.CharField("Option C", max_length=255, null=True)
    option_d      = models.CharField("Option D", max_length=255, null=True)

    correct_choice = models.CharField(
        max_length=1,
        choices=CHOICE_LETTERS,
        help_text="Select A, B, C, or D as the correct answer.",
        null = True
    )

    def __str__(self):
        # e.g. "math Q#12 (A)"
        return f"{self.subject.slug} Q#{self.id} (Correct: {self.correct_choice})"
 
    
class JAMBOption(models.Model):
    """
    A single answer choice for a JAMBQuestion.
    Each option has a label (e.g. "A", "B", "C", "D"), some text,
    and a boolean `is_correct` flag.
    """
    question   = models.ForeignKey(
        JAMBQuestion,
        related_name="options",
        on_delete=models.CASCADE
    )
    label      = models.CharField(max_length=1)   # "A", "B", "C", "D", etc.
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(
        default=False,
        help_text="Mark True for the correct answer"
    )

    def __str__(self):
        return f"{self.label}. {self.text}"


class Strategy(models.Model):
    """
    Exam strategy tips (e.g. Time Management Tips, Answering Techniques, etc.).
    """
    category = models.CharField(max_length=100)   # e.g. "Time Management Tips"
    content  = models.TextField()                 # long text with bullet points or paragraphs

    def __str__(self):
        return self.category
