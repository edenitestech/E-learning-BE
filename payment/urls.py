from django.urls import path
from . import views

urlpatterns = [
    path('initialize/', views.InitializePaymentView.as_view(), name='payment-initialize'),
    path('verify/<str:reference>/', views.VerifyPaymentView.as_view(), name='payment-verify'),
    path('webhook/', views.WebhookPaymentView.as_view(), name='payment-webhook'),
]
