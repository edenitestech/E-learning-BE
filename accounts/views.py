# accounts/views.py
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    FullDataExportSerializer,
    UserDataExportSerializer,
)
from courses.models import Course
from courses.serializers import CourseSerializer
from enrollments.models import Enrollment, LessonProgress, Answer
from enrollments.serializers import (
    EnrollmentSerializer,
    LessonProgressSerializer,
    AnswerSerializer,
)

# Create your views here.

User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            # Return the validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(ProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Provide Data-Access & Erasure Endpoints (GDPR-Style)
class GDPRDataExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_view_name(self):
        return "Personal Data Export"

    def get_view_description(self, html=False):
        return (
            "Download a JSON dump of all your user profile, "
            "enrollments, progress and quiz answers."
        )

    def get(self, request):
        user = request.user

        # Gather all related data
        courses     = Course.objects.filter(instructor=user)
        enrollments = Enrollment.objects.filter(student=user)
        progress    = LessonProgress.objects.filter(enrollment__student=user)
        answers     = Answer.objects.filter(student=user)

        # Serialize into a single payload
        serializer = FullDataExportSerializer({
            "user":        UserDataExportSerializer(user).data,
            "courses":     CourseSerializer(courses, many=True).data,
            "enrollments": EnrollmentSerializer(enrollments, many=True).data,
            "progress":    LessonProgressSerializer(progress, many=True).data,
            "answers":     AnswerSerializer(answers, many=True).data,
        })

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GDPRDeleteAccountView(APIView):
    name = "Delete Users Account"
    permission_classes = [permissions.IsAuthenticated]
    

    def delete(self, request):
        user = request.user
        # Soft‐delete / anonymize
        user.username = f"deleted_user_{user.id}"
        user.email = ""
        user.set_unusable_password()
        user.is_active = False
        user.save()
        # Remove related PII
        Enrollment.objects.filter(student=user).delete()
        LessonProgress.objects.filter(enrollment__student=user).delete()
        Answer.objects.filter(student=user).delete()
        return Response({"detail": "Account deactivated and personal data removed."}, status=status.HTTP_204_NO_CONTENT)
    



