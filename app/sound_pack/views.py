from rest_framework import viewsets, authentication, permissions
from core.models import SoundPack
from .serializers import SoundPackSerializer


class SoundPackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SoundPack.objects.all()
    serializer_class = SoundPackSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class AdminSoundPackViewSet(viewsets.ModelViewSet):
    queryset = SoundPack.objects.all()
    serializer_class = SoundPackSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
