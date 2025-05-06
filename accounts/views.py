# accounts/views.py
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, ProfileSerializer

from .serializers import (RegisterSerializer, ProfileSerializer,FullDataExportSerializer,UserDataExportSerializer,)
from courses.models import Course
from courses.serializers import CourseSerializer
from enrollments.models import Enrollment, LessonProgress, Answer
from enrollments.serializers import (EnrollmentSerializer, LessonProgressSerializer, AnswerSerializer,)

# Create your views here.

User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create the user
        user = serializer.save()

        # 2. Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access  = str(refresh.access_token)
        refresh = str(refresh)

        # 3. Serialize user profile
        user_data = ProfileSerializer(user).data

        # 4. Return both user and tokens
        return Response(
            {
                "user":    user_data,
                "access":  access,
                "refresh": refresh,
            },
            status=status.HTTP_201_CREATED
        )


# profile views
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
# Dashboard views
class DashboardView(APIView):
    """
    GET /api/auth/dashboard/
    - If student: list enrolled courses + progress per course.
    - If instructor: list own courses + enrollment counts.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_instructor:
            # Instructor dashboard
            courses = Course.objects.filter(instructor=user).annotate(
                num_students=Count('enrollment')
            )
            data = {
                "role": "instructor",
                "courses": CourseSerializer(courses, many=True).data,
                "enrollment_stats": {
                    c.id: c.num_students for c in courses
                }
            }
        else:
            # Student dashboard
            enrollments = Enrollment.objects.filter(student=user)
            # For each enrollment, count completed lessons
            progress = LessonProgress.objects.filter(
                enrollment__in=enrollments, completed=True
            )
            # Group count by enrollment.course
            completed_counts = (
                progress
                .values("enrollment__course")
                .annotate(completed_lessons=Count("id"))
            )
            data = {
                "role": "student",
                "enrollments": EnrollmentSerializer(enrollments, many=True).data,
                "progress_summary": {
                    item["enrollment__course"]: item["completed_lessons"]
                    for item in completed_counts
                }
            }

        return Response(data, status=status.HTTP_200_OK)

# Logout views
class LogoutView(APIView):
    """
    Blacklist the refresh token so it—and its associated access token—can no longer be used.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required to log out."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_205_RESET_CONTENT
        )
    
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
    



