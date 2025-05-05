from django.urls import path
from syncodeapp.views.assignment_views import (
   add_assignment,
   get_assignment,
   get_assignments_by_course,
   submit_assignment,
   get_assignment_status
)

urlpatterns = [
    path('add-assignment/',add_assignment,name='add-assignment'),
    path('get-assignment',get_assignment,name='get-assignment'),
    path('get-assignments-by-course',get_assignments_by_course,name='get-assignments-by-course'),
    path('submit-assignment/',submit_assignment,name='submit-assignment'),
    path('get-assignment-status',get_assignment_status,name='get-assignment-status'),
]