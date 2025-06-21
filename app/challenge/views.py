from rest_framework import viewsets, permissions, authentication, status
from .serializers import ChallengeSerializer, VoiceUpdateSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from core.models import Challenge


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return challenges created by the requesting user
        return Challenge.objects.filter(created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == 'update_voice':
            return VoiceUpdateSerializer
        return ChallengeSerializer

    @action(detail=True, methods=['patch'], url_path='voice', parser_classes=[MultiPartParser, FormParser])
    def update_voice(self, request, pk=None):
        """Update voice/audio for an existing challenge by uploading a .wav file"""
        challenge = self.get_object()

        # Check if user owns this challenge (optional security check)
        if challenge.created_by != request.user:
            return Response(
                {"error": "You don't have permission to update this challenge."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = VoiceUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                updated_challenge = serializer.update_challenge_voice(challenge)
                # Return the updated challenge data
                response_serializer = ChallengeSerializer(updated_challenge)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
