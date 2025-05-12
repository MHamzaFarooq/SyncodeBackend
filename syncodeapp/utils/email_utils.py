import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP is {otp}. It is valid for 10 minutes."
    send_mail(subject, message, 'hamzafarooq49ml@gmail.com', [email])
