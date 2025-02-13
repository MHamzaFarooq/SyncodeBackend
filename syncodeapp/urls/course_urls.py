from django.urls import path
from syncodeapp.views.course_views import create_course,get_all_courses,get_available_courses,get_upcoming_courses

urlpatterns = [
    path('create-course/',create_course,name='create-course'),
    path('get-all/',get_all_courses,name='get-all-courses'),
    path('get-available/',get_available_courses,name='get-available-courses'),
    path('get-upcoming/',get_upcoming_courses,name='get-upcoming-courses'),
]