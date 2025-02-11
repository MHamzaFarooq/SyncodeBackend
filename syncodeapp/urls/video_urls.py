from django.urls import path
from syncodeapp.views.video_views import create_video

urlpatterns = [
    path('create-video/',create_video,name='create-video')
]