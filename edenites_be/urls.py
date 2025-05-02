"""
URL configuration for edenites_be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from courses.views import CategoryViewSet, CourseViewSet
from content.views import LessonViewSet, QuestionViewSet
from enrollments.views import EnrollmentViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("courses", CourseViewSet)
router.register("lessons", LessonViewSet)
router.register("questions", QuestionViewSet)
router.register("enrollments", EnrollmentViewSet, basename="enrollments")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("content.urls")),
    path("api/", include("enrollments.urls")),
    path("api/", include("courses.urls")),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
