# accounts.models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_cryptography.fields import encrypt

# Create your models here.

class User(AbstractUser):
    is_instructor = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
