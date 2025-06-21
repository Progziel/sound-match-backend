import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from core.models import Message, Room
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to room: {self.room_name}'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')

            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def handle_chat_message(self, data):
        message = data.get('message', '')
        email = data.get('email', 'Anonymous')

        if not message.strip():
            return

        # Save message to database
        await self.save_message(email, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'email': email,
                'timestamp': str(timezone.now())
            }
        )

    async def handle_typing(self, data):
        email = data.get('email', 'Anonymous')
        is_typing = data.get('is_typing', False)

        # Broadcast typing status to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'email': email,
                'is_typing': is_typing
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'email': event['email'],
            'timestamp': event['timestamp']
        }))

    async def typing_status(self, event):
        # Send typing status to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'email': event['email'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def save_message(self, email, message):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        room, created = Room.objects.get_or_create(name=self.room_name)

        Message.objects.create(
            room=room,
            user=user,
            email=email,
            content=message
        )
