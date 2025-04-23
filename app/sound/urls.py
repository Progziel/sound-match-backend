"""URL mappings for the sound API."""
from django.urls import path
from .views import SoundViewSet

app_name = 'sound'

urlpatterns = [
    path('sounds/',
         SoundViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='sounds'),
    path('sounds/<int:pk>/',
         SoundViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name='sound-detail'),
]
