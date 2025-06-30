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
    UserDataExportSerializer, ProfileSerializer
)
from courses.models import Course
from courses.serializers import CourseSerializer
from enrollments.models import Enrollment, LessonProgress, Answer
from enrollments.serializers import (
    EnrollmentSerializer,
    LessonProgressSerializer,
    AnswerSerializer,
)
from rest_framework import viewsets
from .models import Notification, Message
from .serializers import NotificationSerializer, MessageSerializer

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
        response_data = {}  # <- Make sure this is a dict

        if user.is_instructor:
            # Instructor side
            courses = (
                Course.objects.filter(instructor=user)
                .annotate(num_students=Count("orders"))
            )
            response_data["role"] = "instructor"
            response_data["courses"] = CourseSerializer(courses, many=True).data
            response_data["enrollment_stats"] = {
                c.id: c.num_students for c in courses
            }

        else:
            # Student side
            enrollments = Enrollment.objects.filter(student=user)
            completed = (
                LessonProgress.objects
                .filter(enrollment__in=enrollments, completed=True)
                .values("enrollment__course")
                .annotate(completed_lessons=Count("id"))
            )
            response_data["role"] = "student"
            response_data["enrollments"] = EnrollmentSerializer(
                enrollments, many=True
            ).data
            response_data["progress_summary"] = {
                item["enrollment__course"]: item["completed_lessons"]
                for item in completed
            }

        # Optional: add user’s own name/email to dashboard payload
        response_data["user"] = {
            "first_name": user.first_name,
            "last_name":  user.last_name,
            "email":      user.email,
        }

        # TODO: Hook up your real notifications/messages logic here.
        # For now, stub out empty lists so the front‑end doesn’t blow up:
        response_data["notifications"] = []
        response_data["inbox"]         = []

        return Response(response_data, status=status.HTTP_200_OK)

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

class NotificationViewSet(viewsets.ModelViewSet):
    """
    List and mark notifications as read.
    """
    serializer_class   = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_update(self, serializer):
        # support marking as read
        serializer.instance.is_read = serializer.validated_data.get("is_read", True)
        serializer.instance.save()
        return serializer

class MessageViewSet(viewsets.ModelViewSet):
    """
    Send messages and list received messages.
    """
    serializer_class = MessageSerializer

    def get_permissions(self):
        # Only authenticated users may send/read
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user).order_by("-sent_at")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)