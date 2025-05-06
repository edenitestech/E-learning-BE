# accounts.urls
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, 
    ProfileView, 
    GDPRDataExportView, 
    GDPRDeleteAccountView,
    LogoutView, 
    )

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("gdpr/export/", GDPRDataExportView.as_view(), name="gdpr-export"),
    path("gdpr/delete/", GDPRDeleteAccountView.as_view(), name="gdpr-delete"),
    path("logout/", LogoutView.as_view(), name="logout"),

]
