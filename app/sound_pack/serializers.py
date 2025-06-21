from rest_framework import serializers
from core.models import SoundPack


class SoundPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoundPack
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
