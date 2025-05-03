from rest_framework import serializers
from .models import Category, Course, Order

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "instructor"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Order
        fields = ["id", "course", "amount", "status", "transaction_id", "created_at"]
        read_only_fields = ["status", "transaction_id", "created_at"]