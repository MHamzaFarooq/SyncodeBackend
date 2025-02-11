from django.urls import path
from syncodeapp.views.course_views import create_course

urlpatterns = [
    path('create-course/',create_course,name='create-course')
]