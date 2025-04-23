from rest_framework import serializers
from core.models.sound import Sound


class SoundSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Sound
        fields = '__all__'
