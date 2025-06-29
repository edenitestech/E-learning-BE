# auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Custom backend that allows authentication via either email or username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # If 'username' wasn’t provided, pick it up from 'email' kwarg
        if username is None:
            username = kwargs.get("email", None)

        # Now if username is still None or password is None, we bail out
        if not username or not password:
            return None

        # At this point, 'username' is a non‐empty string. Check if it contains '@'.
        if "@" in username:
            lookup_field = "email"
        else:
            lookup_field = "username"

        try:
            user_obj = User.objects.get(**{lookup_field: username})
        except User.DoesNotExist:
            return None

        # Verify password and that the user is not inactive
        if user_obj.check_password(password) and self.user_can_authenticate(user_obj):
            return user_obj

        return None
