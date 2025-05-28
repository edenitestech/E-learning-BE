# accounts/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # `username` here will be the email they submitted
        lookup = {"email": username} if "@" in username else {"username": username}
        try:
            user = User.objects.get(**lookup)
        except User.DoesNotExist:
            return None
        return user if user.check_password(password) and self.user_can_authenticate(user) else None
