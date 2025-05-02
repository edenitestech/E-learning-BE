# accounts.urls
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, GDPRDataExportView, GDPRDeleteAccountView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("gdpr/export/", GDPRDataExportView.as_view(), name="gdpr-export"),
    path("gdpr/delete/", GDPRDeleteAccountView.as_view(), name="gdpr-delete"),
]
