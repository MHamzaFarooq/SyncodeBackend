from django.urls import path
from syncodeapp.views.csrf_views import get_csrf_token

urlpatterns = [
    path('get-csrftoken/',get_csrf_token,name='get-csrf-token')
]