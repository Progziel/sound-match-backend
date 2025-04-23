from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from rest_framework import authentication, permissions
from rest_framework.viewsets import ModelViewSet
from core.models.sound import Sound
from .serializers import SoundSerializer


class SoundViewSet(ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Sound.objects.all()
    serializer_class = SoundSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """Ensure `created_by` is set before saving"""
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        """Ensure users can only delete their own sounds"""
        if instance.created_by != self.request.user:
            raise PermissionDenied(
                "You do not have permission to delete this sound.")
        instance.delete()
