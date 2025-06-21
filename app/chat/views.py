from rest_framework import viewsets, status
# , permissions, authentication
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.models import Room, Message
from .serializers import RoomSerializer, RoomListSerializer, MessageSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return RoomListSerializer
        return RoomSerializer

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a specific room"""
        room = get_object_or_404(Room, pk=pk)
        messages = room.messages.all()

        # Pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a room via REST API"""
        room = get_object_or_404(Room, pk=pk)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(
                room=room,
                user=request.user,
                email=request.user.email
            )

            # You could also broadcast this message via WebSocket here
            # using channels.layers.get_channel_layer()

            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Message.objects.all()
        room_id = self.request.query_params.get('room', None)
        if room_id is not None:
            queryset = queryset.filter(room_id=room_id)
        return queryset