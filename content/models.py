from django.db import models
from django.forms import JSONField

from courses.models import Course

# Create your models here.

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to="videos/")

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    text = models.TextField()
    choices = JSONField()  
    correct_choice = models.CharField(max_length=1)
    explanation = models.TextField()
