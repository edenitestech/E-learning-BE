# testimonials/models.py

from django.db import models

class Testimonial(models.Model):
    """
    Student or user testimonials (feedback).
    """
    name       = models.CharField(max_length=100)
    role       = models.CharField(max_length=100)   # e.g. "Software Developer"
    avatar_url = models.URLField(blank=True)        # e.g. "https://randomuser.me/…/men/32.jpg"
    quote      = models.TextField()
    rating     = models.PositiveSmallIntegerField(default=0)  # 1..5 stars

    def __str__(self):
        return f"{self.name} ({self.rating}★)"
