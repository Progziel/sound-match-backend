"""URL mappings for the challenge API."""
from django.urls import path
from .views import ChallengeViewSet

app_name = 'challenge'

urlpatterns = [
    path('challenges/',
         ChallengeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='challenges'),
    path('challenges/<int:pk>/',
         ChallengeViewSet.as_view({
             'get': 'retrieve',
             'patch': 'partial_update'
            }),
         name='challenge-detail'),
]
