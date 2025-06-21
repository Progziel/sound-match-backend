"""User Views"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from user.serializers import (
    SignupSerializer,
    LoginSerializer,
    ManageUserSerializer,
    UpdatePasswordSerializer,
    UserSearchSerializer
)


class SignupView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        """Override create method to return success/failure status."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'User registered successfully'
        }, status=201)


class LoginView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = LoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        """Override post method to return token and user data."""
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            }
        })


class ManageUserView(generics.GenericAPIView):
    """Manage the authenticated user with GET and PATCH methods."""
    serializer_class = ManageUserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve the authenticated user."""
        return self.request.user

    def get(self, request, *args, **kwargs):
        """Handle GET requests to retrieve user details."""
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=200)

    def patch(self, request, *args, **kwargs):
        """Handle PATCH requests to update user details."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


class UpdatePasswordView(generics.GenericAPIView):
    """View to manage password updates for authenticated users."""
    serializer_class = UpdatePasswordSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve the authenticated user."""
        return self.request.user

    def patch(self, request, *args, **kwargs):
        """Handle PATCH request to update the user's password."""
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class UserSearchView(generics.GenericAPIView):
    """Search for users by email address."""
    serializer_class = UserSearchSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle GET request to search user by email."""
        email = request.query_params.get('email', None)

        if not email:
            return Response({
                'error': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = get_user_model().objects.get(email__iexact=email)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except get_user_model().DoesNotExist:
            return Response({
                'error': 'User not found with the provided email'
            }, status=status.HTTP_404_NOT_FOUND)