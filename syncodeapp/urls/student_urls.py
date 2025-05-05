from django.urls import path
from syncodeapp.views.student_views import create_student, login_student,logout_student,get_student_submissions,get_student_feedback_submissions

urlpatterns = [
    path('create-student/',create_student,name='create-student'),
    path('login-student/',login_student,name='login-student'),
    path('logout-student/',logout_student,name='logout-student'),
    path('get-student-submissions',get_student_submissions,name='get-student-submissions'),
    path('get-student-feedback-submissions',get_student_feedback_submissions,name='get-student-feedback-submissions'),

]