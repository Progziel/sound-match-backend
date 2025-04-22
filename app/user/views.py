"""User Views"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from user.serializers import (
    UserSerializer,
    TokenSerializer,
    ManageUserSerializer,
    UpdatePasswordSerializer
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class LoginView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


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
