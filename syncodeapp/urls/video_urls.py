from django.urls import path
from syncodeapp.views.video_views import create_video, get_video, delete_video

urlpatterns = [
    path('create-video/',create_video,name='create-video'),
    path('get-video',get_video,name='get-video'),
    path('delete-video/',delete_video,name='delete-video')
]