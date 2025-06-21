"""URL mappings for the challenge API."""
from django.urls import path
from .views import ChallengeViewSet

app_name = 'challenge'

urlpatterns = [
    path('',
         ChallengeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='challenges'),
    path('<int:pk>/',
         ChallengeViewSet.as_view(
             {'get': 'retrieve','patch': 'partial_update'}),
         name='challenge-detail'),
    path('<int:pk>/voice/',
         ChallengeViewSet.as_view({'patch': 'update_voice'}),
         name='challenge-voice'),
]
