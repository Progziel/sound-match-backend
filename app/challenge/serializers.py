from rest_framework import serializers
from core.models import Challenge


class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = '__all__'
        read_only_fields = ["created_at", "updated_at"]

    def validate_levels(self, value):
        """Ensure levels is a list of float values between 0 and 1"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Levels must be a list.")
        if not all(isinstance(v, (float, int)) and 0 <= v <= 1 for v in value):
            raise serializers.ValidationError(
                "All values in levels must be floating-point "
                "numbers between 0 and 1.")
        return value
