from django.urls import path
from syncodeapp.views.teacher_views import create_teacher, login_teacher,logout_teacher, add_feedback, get_teacher_submissions

urlpatterns = [
    path('create-teacher/',create_teacher,name='create-teacher'),
    path('login-teacher/',login_teacher,name='login-teacher'),
    path('logout-teacher/',logout_teacher,name='logout-teacher'),
    path('add-feedback/',add_feedback,name='add-feedback/'),
    path('get-teacher-submissions',get_teacher_submissions,name='get-teacher-submissions'),
]