# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MyTokenObtainPairView,
    RegisterView,
    ProfileView,
    DashboardView,
    LogoutView,
    GDPRDataExportView,
    GDPRDeleteAccountView,
)

urlpatterns = [
    path("login/",        MyTokenObtainPairView.as_view(),    name="token_obtain_pair"),
    path("token/refresh/",TokenRefreshView.as_view(),         name="token_refresh"),
    path("register/",     RegisterView.as_view(),             name="register"),
    path("profile/",      ProfileView.as_view(),              name="profile"),
    path("dashboard/",    DashboardView.as_view(),            name="dashboard"),
    path("logout/",       LogoutView.as_view(),               name="logout"),
    path("gdpr/export/",  GDPRDataExportView.as_view(),        name="gdpr-export"),
    path("gdpr/delete/",  GDPRDeleteAccountView.as_view(),     name="gdpr-delete"),
]
