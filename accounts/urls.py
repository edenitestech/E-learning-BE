# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    MyTokenObtainPairView,
    RegisterView,
    ProfileView,
    DashboardView,
    LogoutView,
    GDPRDataExportView,
    GDPRDeleteAccountView,
    NotificationViewSet,
    MessageViewSet,
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
router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"messages",      MessageViewSet,      basename="message")

urlpatterns += router.urls