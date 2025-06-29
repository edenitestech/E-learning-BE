# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_backends import EmailOrUsernameBackend
from courses.serializers import CourseSerializer
from enrollments.serializers import (
    EnrollmentSerializer,
    LessonProgressSerializer,
    AnswerSerializer,
)

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Registers a new user (splitting 'fullname' into first/last),
    stores email as both email and username, returns the user instance.
    """
    fullname        = serializers.CharField(write_only=True)
    email           = serializers.EmailField()
    password        = serializers.CharField(write_only=True, min_length=8)
    confirmPassword = serializers.CharField(write_only=True, min_length=8)
    is_instructor   = serializers.BooleanField(default=False)

    def validate_email(self, email):
        # Check if any user already has this email
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return email

    def validate(self, data):
        if data["password"] != data["confirmPassword"]:
            raise serializers.ValidationError({"confirmPassword": "Passwords do not match."})
        return data

    def create(self, validated_data):
        fullname = validated_data.pop("fullname")
        parts = fullname.strip().split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""

        user = User(
            username=validated_data["email"],  # Use email as username
            email=validated_data["email"],
            first_name=first,
            last_name=last,
            is_instructor=validated_data.get("is_instructor", False),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_instructor", "first_name", "last_name")
        read_only_fields = ("id", "is_instructor")


class UserDataExportSerializer(serializers.ModelSerializer):
    """
    Used for the GDPR export: returns basic user fields.
    """
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_instructor"]


class FullDataExportSerializer(serializers.Serializer):
    """
    Bundles together all the user’s related data for GDPR export.
    """
    user = UserDataExportSerializer()
    courses = CourseSerializer(many=True)          # courses they created (if instructor)
    enrollments = EnrollmentSerializer(many=True)  # courses they’re enrolled in
    progress = LessonProgressSerializer(many=True) # lesson progress records
    answers = AnswerSerializer(many=True)          # their quiz answers


class MyTokenObtainPairSerializer(serializers.Serializer):
    """
    Custom “login” serializer that accepts either 'email' or 'username' + 'password'.
    Returns 'access' + 'refresh' tokens on success.
    """
    username = serializers.CharField(required=False, write_only=True)
    email    = serializers.EmailField(required=False, write_only=True)
    password = serializers.CharField(write_only=True)

    access  = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        raw_username = attrs.get("username")
        raw_email    = attrs.get("email")
        raw_password = attrs.get("password")

        if not raw_password:
            raise serializers.ValidationError({"detail": "Password is required."})

        if raw_username:
            lookup_value = raw_username
        elif raw_email:
            lookup_value = raw_email
        else:
            raise serializers.ValidationError(
                {"detail": "Must include either 'email' or 'username' and 'password'."}
            )

        # Call our custom backend
        user = EmailOrUsernameBackend().authenticate(
            request=self.context.get("request"),
            username=lookup_value,
            password=raw_password,
        )

        if user is None:
            raise AuthenticationFailed(
                {"detail": "No active user found with the given credentials."}
            )

        # Generate tokens
        refresh_token_obj = RefreshToken.for_user(user)
        access_token_str  = str(refresh_token_obj.access_token)
        refresh_token_str = str(refresh_token_obj)

        return {
            "refresh": refresh_token_str,
            "access":  access_token_str,
        }
