from django.urls import reverse, NoReverseMatch
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import StaticHTMLRenderer


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([StaticHTMLRenderer])
def api_plaintext_overview(request):
    """
    Return a plain‐text list of all API endpoints (method + path).
    """

    endpoints = []

    # ────── Auth / Accounts ─────────────────────────────
    try: endpoints.append(f"POST   {reverse('token_obtain_pair')}")     # /api/auth/login/
    except NoReverseMatch: pass
    try: endpoints.append(f"POST   {reverse('token_refresh')}")         # /api/auth/token/refresh/
    except NoReverseMatch: pass
    try: endpoints.append(f"POST   {reverse('logout')}")                # /api/auth/logout/
    except NoReverseMatch: pass
    try: endpoints.append(f"POST   {reverse('register')}")              # /api/auth/register/
    except NoReverseMatch: pass
    try: endpoints.append(f"GET    {reverse('profile')}")               # /api/auth/profile/
    except NoReverseMatch: pass
    try: endpoints.append(f"PUT    {reverse('profile')}")               # /api/auth/profile/
    except NoReverseMatch: pass
    try: endpoints.append(f"GET    {reverse('dashboard')}")             # /api/auth/dashboard/
    except NoReverseMatch: pass
    try: endpoints.append(f"GET    {reverse('gdpr-export')}")           # /api/auth/gdpr/export/
    except NoReverseMatch: pass
    try: endpoints.append(f"DELETE {reverse('gdpr-delete')}")           # /api/auth/gdpr/delete/
    except NoReverseMatch: pass

    # ────── Testimonials ────────────────────────────────
    try: endpoints.append(f"GET    {reverse('testimonial-list')}")      # /api/testimonials/
    except NoReverseMatch: pass
    try: endpoints.append(f"POST   {reverse('testimonial-list')}")      # /api/testimonials/
    except NoReverseMatch: pass
    try: endpoints.append(f"GET    {reverse('testimonial-detail', args=[1])}")
    except NoReverseMatch: pass
    try: endpoints.append(f"PUT    {reverse('testimonial-detail', args=[1])}")
    except NoReverseMatch: pass
    try: endpoints.append(f"PATCH  {reverse('testimonial-detail', args=[1])}")
    except NoReverseMatch: pass
    try: endpoints.append(f"DELETE {reverse('testimonial-detail', args=[1])}")
    except NoReverseMatch: pass

    # ────── Courses / Categories ────────────────────────
    endpoints += [
        "GET    /api/categories/",
        "POST   /api/categories/",
        "GET    /api/categories/<id>/",
        "PUT    /api/categories/<id>/",
        "PATCH  /api/categories/<id>/",
        "DELETE /api/categories/<id>/",

        "GET    /api/courses/",
        "POST   /api/courses/",
        "GET    /api/courses/<id>/",
        "PUT    /api/courses/<id>/",
        "PATCH  /api/courses/<id>/",
        "DELETE /api/courses/<id>/",

        # Nested: Lessons
        "GET    /api/courses/<id>/lessons/",
        "POST   /api/courses/<id>/lessons/",
        "PUT    /api/courses/<id>/lessons/<lesson_id>/",
        "PATCH  /api/courses/<id>/lessons/<lesson_id>/",
        "DELETE /api/courses/<id>/lessons/<lesson_id>/",

        # Nested: Quizzes
        "GET    /api/courses/<id>/quizzes/",
        "POST   /api/courses/<id>/quizzes/",
        "PUT    /api/courses/<id>/quizzes/<quiz_id>/",
        "PATCH  /api/courses/<id>/quizzes/<quiz_id>/",
        "DELETE /api/courses/<id>/quizzes/<quiz_id>/",

        # Exam/Project submission
        "POST   /api/courses/<id>/exam-project/",
        "POST   /api/courses/<id>/exam-project/<submission_id>/approve/",

        # Purchase
        "POST   /api/courses/<id>/purchase/",
    ]

    # ────── Lessons (standalone) ────────────────────────
    endpoints += [
        "GET    /api/lessons/",
        "POST   /api/lessons/",
        "GET    /api/lessons/<id>/",
        "PUT    /api/lessons/<id>/",
        "PATCH  /api/lessons/<id>/",
        "DELETE /api/lessons/<id>/",
    ]

    # ────── Questions (standalone follow-up) ────────────
    endpoints += [
        "GET    /api/questions/",
        "POST   /api/questions/",
        "GET    /api/questions/<id>/",
        "PUT    /api/questions/<id>/",
        "PATCH  /api/questions/<id>/",
        "DELETE /api/questions/<id>/",

        # Extra actions
        "POST   /api/questions/<id>/answer/",
        "GET    /api/questions/<id>/explanation/",
    ]

    # ────── Enrollments ─────────────────────────────────
    endpoints += [
        "GET    /api/enrollments/",
        "POST   /api/enrollments/",
        "GET    /api/enrollments/<id>/",
        "PUT    /api/enrollments/<id>/",
        "PATCH  /api/enrollments/<id>/",
        "DELETE /api/enrollments/<id>/",
    ]

    # ────── Lesson Progress ─────────────────────────────
    endpoints += [
        "GET    /api/progress/",
        "POST   /api/progress/",
        "GET    /api/progress/<id>/",
        "PUT    /api/progress/<id>/",
        "PATCH  /api/progress/<id>/",
        "DELETE /api/progress/<id>/",
    ]

    # ────── Answers ─────────────────────────────────────
    endpoints += [
        "GET    /api/answers/",
        "POST   /api/answers/",
        "GET    /api/answers/<id>/",
        "PUT    /api/answers/<id>/",
        "PATCH  /api/answers/<id>/",
        "DELETE /api/answers/<id>/",
    ]

    # ────── Exams / Past Questions ──────────────────────
    endpoints += [
        "GET    /api/exams/past-questions/",
        "POST   /api/exams/past-questions/",
        "GET    /api/exams/past-questions/<id>/",
        "PUT    /api/exams/past-questions/<id>/",
        "PATCH  /api/exams/past-questions/<id>/",
        "DELETE /api/exams/past-questions/<id>/",

        # Quiz mode
        "POST   /api/exams/past-questions/quiz/",
        # Practice mode
        "POST   /api/exams/past-questions/practice/",
    ]

    # ────── Payments ────────────────────────────────────
    endpoints += [
        "POST   /api/payments/purchase/<course_id>/",
        "POST   /api/payments/webhook/",
        "GET    /api/payments/verify/<order_id>/",
    ]

    # Join everything
    text = "\n".join(endpoints)
    return HttpResponse(text, content_type="text/plain")
