from django.conf import settings
from django.db import models
from decimal import Decimal

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))


class Order(models.Model):
    PENDING   = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED    = "FAILED"
    STATUS_CHOICES = [
        (PENDING,   "Pending"),
        (COMPLETED, "Completed"),
        (FAILED,    "Failed"),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
