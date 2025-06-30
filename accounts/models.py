# accounts.models
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_cryptography.fields import encrypt

# Create your models here.

class User(AbstractUser):
    is_instructor = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

class Notification(models.Model):
    """
    A one‑way notification to a user (e.g. “Your quiz is due”).
    """
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    verb      = models.CharField(max_length=255)       # e.g. "New lesson available"
    created_at = models.DateTimeField(auto_now_add=True)
    is_read   = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.verb[:20]}…"

class Message(models.Model):
    """
    A two‑way message between users (e.g. student ⇄ instructor).
    """
    sender    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    subject   = models.CharField(max_length=255)
    body      = models.TextField()
    sent_at   = models.DateTimeField(auto_now_add=True)
    is_read   = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.subject}"