from django.urls import path
from syncodeapp.views.teacher_views import create_teacher, login_teacher,logout_teacher

urlpatterns = [
    path('create-teacher/',create_teacher,name='create-teacher'),
    path('login-teacher/',login_teacher,name='login-teacher'),
    path('logout-teacher/',logout_teacher,name='logout-teacher')
]