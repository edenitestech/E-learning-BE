# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.auth_backends import EmailOrUsernameBackend
from courses.serializers import CourseSerializer
from enrollments.serializers import EnrollmentSerializer, LessonProgressSerializer, AnswerSerializer
from content.serializers import LessonSerializer, QuestionSerializer

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    fullname = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirmPassword = serializers.CharField(write_only=True, min_length=8)
    is_instructor = serializers.BooleanField(default=False)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return email

    def validate(self, data):
        if data["password"] != data["confirmPassword"]:
            raise serializers.ValidationError({"confirmPassword": "Passwords do not match."})
        return data

    def create(self, validated_data):
        # Split fullname into first and last (naïvely)
        fullname = validated_data.pop("fullname")
        parts     = fullname.strip().split(" ", 1)
        first, last = parts[0], parts[1] if len(parts) > 1 else ""

        user = User(
            username=validated_data["email"],   # use email as username
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
    # include user’s own fields
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_instructor"]

class FullDataExportSerializer(serializers.Serializer):
    user       = UserDataExportSerializer()
    courses    = CourseSerializer(many=True)          # courses they created, if instructor
    enrollments = EnrollmentSerializer(many=True)     # courses they’re enrolled in
    progress    = LessonProgressSerializer(many=True) # lesson progress records
    answers     = AnswerSerializer(many=True)         # their quiz answers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  
    identifier = serializers.CharField() # email or username
    password   = serializers.CharField()

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password   = attrs.get("password")

        # Use our custom backend to authenticate
        user = EmailOrUsernameBackend().authenticate(
            request=self.context.get("request"),
            username=identifier,
            password=password
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials", code="authorization")

        # Now populate the token
        data = super().get_token(user)
        return {
            "refresh": str(data),
            "access":  str(data.access_token),
        }