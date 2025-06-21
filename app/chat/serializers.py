from rest_framework import serializers
from core.models import Room, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'email', 'content', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class RoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'created_at', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class RoomListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'created_at', 'message_count', 'last_message']
        read_only_fields = ['id', 'created_at']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content,
                'email': last_msg.email,
                'timestamp': last_msg.timestamp
            }
        return None