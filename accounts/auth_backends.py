# accounts/auth_backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Authenticate either by username or by email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # ‘username’ may actually be email
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        # Try looking up by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Fallback to looking up by email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None

        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
