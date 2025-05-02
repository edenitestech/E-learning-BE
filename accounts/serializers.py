# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from courses.serializers import CourseSerializer
from enrollments.serializers import EnrollmentSerializer, LessonProgressSerializer, AnswerSerializer
from content.serializers import LessonSerializer, QuestionSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ("username", "email", "password", "is_instructor")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            is_instructor=validated_data.get("is_instructor", False)
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