# accounts/views.py

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    MyTokenObtainPairSerializer,
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

User = get_user_model()


class MyTokenObtainPairView(APIView):
    """
    POST /api/auth/login/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MyTokenObtainPairSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        # validated_data contains {"access": ..., "refresh": ...}
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    POST /api/auth/register/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        refresh_obj   = RefreshToken.for_user(user)
        access_token  = str(refresh_obj.access_token)
        refresh_token = str(refresh_obj)

        user_data = ProfileSerializer(user).data

        return Response(
            {
                "user":    user_data,
                "access":  access_token,
                "refresh": refresh_token,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileView(APIView):
    """
    GET  /api/auth/profile/  → return current user’s profile
    PUT  /api/auth/profile/  → update the profile fields
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DashboardView(APIView):
    """
    GET /api/auth/dashboard/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_instructor:
            # Instructor: list own courses + enrollment counts
            courses = Course.objects.filter(instructor=user).annotate(
                num_students=Count("orders")  # orders → enrollments happen on successful payment
            )
            data = {
                "role": "instructor",
                "courses": CourseSerializer(courses, many=True).data,
                "enrollment_stats": {c.id: c.num_students for c in courses},
            }
        else:
            # Student: list enrolled courses + progress counts
            enrollments = Enrollment.objects.filter(student=user)
            progress = LessonProgress.objects.filter(
                enrollment__in=enrollments, completed=True
            )
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
                },
            }

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
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


class GDPRDataExportView(APIView):
    """
    GET /api/auth/gdpr/export/
    """
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
        courses = Course.objects.filter(instructor=user)
        enrollments = Enrollment.objects.filter(student=user)
        progress = LessonProgress.objects.filter(enrollment__student=user)
        answers = Answer.objects.filter(student=user)

        payload = {
            "user":        UserDataExportSerializer(user).data,
            "courses":     CourseSerializer(courses, many=True).data,
            "enrollments": EnrollmentSerializer(enrollments, many=True).data,
            "progress":    LessonProgressSerializer(progress, many=True).data,
            "answers":     AnswerSerializer(answers, many=True).data,
        }

        serializer = FullDataExportSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GDPRDeleteAccountView(APIView):
    """
    DELETE /api/auth/gdpr/delete/
    Soft‐delete the user by anonymizing and removing PII.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.username = f"deleted_user_{user.id}"
        user.email = ""
        user.set_unusable_password()
        user.is_active = False
        user.save()

        Enrollment.objects.filter(student=user).delete()
        LessonProgress.objects.filter(enrollment__student=user).delete()
        Answer.objects.filter(student=user).delete()

        return Response(
            {"detail": "Account deactivated and personal data removed."},
            status=status.HTTP_204_NO_CONTENT
        )

