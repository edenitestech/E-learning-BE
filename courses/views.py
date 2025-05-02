from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Course
from .serializers import CourseSerializer
from .models import Category
from .serializers import CategorySerializer
# Create your views here.

from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        # Make sure user is authenticated _and_ marked as instructor
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_instructor", False)
        )

# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, req, view, obj):
#         return obj.owner == req.user  # or obj.owner

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields = ["category", "instructor"]
    search_fields    = ["title", "description"]
    ordering_fields  = ["title", "created_at"]

    def get_permissions(self):
        if self.action in ["create","update","partial_update","destroy"]:
            return [IsInstructor()]
        return [permissions.AllowAny()]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]