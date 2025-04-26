from django.urls import path
from syncodeapp.views.assignment_views import (
   add_assignment,
   get_assignment,
   get_assignments_by_course
)

urlpatterns = [
    path('add-assignment/',add_assignment,name='add-assignment'),
    path('get-assignment',get_assignment,name='get-assignment'),
    path('get-assignments-by-course',get_assignments_by_course,name='get-assignments-by-course'),
]