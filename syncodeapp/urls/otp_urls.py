from django.urls import path
from syncodeapp.views.otp_views import (
    verify_otp_view,
    send_otp_email_view,
    verify_login_otp,
    verify_register_otp,
    resend_otp_view
)

urlpatterns = [
    path('verify-otp/',verify_otp_view,name='verify-otp'),
    path('send-otp/',send_otp_email_view,name='send-otp'),
    path('verify-login-otp/',verify_login_otp,name='verify-login-otp'),
    path('verify-register-otp/',verify_register_otp,name='verify-register-otp/'),
    path('resend-otp-view/',resend_otp_view,name='resend-otp-view'),
]