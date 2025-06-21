"""User Serializers"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


class SignupSerializer(serializers.ModelSerializer):
    """Serializer for user registration and profile editing."""

    class Meta:
        model = get_user_model()
        fields = ['name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError(
                'Unable to authenticate with provided credentials.',
                code='authorization'
            )
        attrs['user'] = user
        return attrs


class ManageUserSerializer(serializers.ModelSerializer):
    """Serializer for managing user details (excluding password)."""

    class Meta:
        model = get_user_model()
        fields = ['name']

    def update(self, instance, validated_data):
        """Update user details."""
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Format the fields in the response."""
        return {
            'id': instance.id,
            'email': instance.email,
            'name': instance.name
        }


class UpdatePasswordSerializer(serializers.Serializer):
    """Serializer for updating the user's password."""
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        min_length=6,  # Ensure a minimum length for security
    )

    def validate(self, attrs):
        """Validate the old password and new password."""
        user = self.context['request'].user
        old_password = attrs.get('old_password')

        # Check if the provided old password matches the user's password
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {'old_password': 'The old password is incorrect.'}
            )

        return attrs

    def update(self, instance, validated_data):
        """Update the user's password."""
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Return a success message in the response."""
        return {'message': 'Password updated successfully.'}


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for searching users by email."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name']
        read_only_fields = ['id', 'email', 'name']