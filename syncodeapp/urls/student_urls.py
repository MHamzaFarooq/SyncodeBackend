from django.urls import path
from syncodeapp.views.student_views import create_student, login_student,logout_student

urlpatterns = [
    path('create-student/',create_student,name='create-student'),
    path('login-student/',login_student,name='login-student'),
    path('logout-student/',logout_student,name='logout-student')
]