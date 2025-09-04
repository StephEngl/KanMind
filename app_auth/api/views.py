"""
Module for user authentication and registration API views and serializers.

This module provides:
- LoginView: Authenticates users and issues authentication tokens.
- RegistrationView: Registers new users with validation and issues tokens.
- UserInfoSerializer: Serializes basic user information including full name.
- RegistrationSerializer: Handles user registration data, password confirmation, and creation.

Example usage:
    from django.urls import path
    from .views import LoginView, RegistrationView

    urlpatterns = [
        path('login/', LoginView.as_view(), name='login'),
        path('registration/', RegistrationView.as_view(), name='registration'),
    ]
"""

# 1. Standard library
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# 2. Third-party
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

# 3. Local imports
from .serializers import RegistrationSerializer, UserInfoSerializer



class LoginView(APIView):
    """
    Summary:
        Authenticates user and returns a token along with user details.

    POST:
        - Authenticates user using email and password.
        - Returns authentication token and user info on success.
        - Returns a 400 response if email or password is missing.
        - Returns a 401 response if credentials are invalid.

    Permissions:
        - AllowAny: No authentication required; open for any user.

    Details:
        - Uses Django's 'authenticate' for login verification.
        - Retrieves user by email, checks password via authentication.
        - Responds with serialized user info and token if successful.
        - Error details are returned in a structured format.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user login by validating email and password and returning authentication token.

        Args: request (Request): DRF Request object with POST data containing 'email' and 'password'.

        Returns: Response: DRF Response with token and user data on success, or error details on failure.
        """
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_obj = User.objects.get(email=email)
        except user_obj.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserInfoSerializer(user)
            data = {
                "token": token.key,
                "fullname": serializer.data['fullname'],
                "email": serializer.data['email'],
                "user_id": serializer.data['id']
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    """
    Summary:
        Registers a new user and returns an authentication token.

    POST:
        - Accepts user data and creates a new user if valid.
        - Returns token and user info on successful registration.
        - Returns serializer errors if validation fails.

    Permissions:
        - AllowAny: No authentication required; open for any user.

    Details:
        - Uses RegistrationSerializer for user creation and validation.
        - Builds response based on serializer's validity.
        - Returns structured data with token and serialized user info.
        - Error messages are returned in a structured format.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles registration of a new user with validation and token issuance.

        Args: request (Request): DRF Request object containing registration data.

        Returns: Response: DRF Response including authentication token and user data when successful,
            or validation errors.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            user_serializer = UserInfoSerializer(saved_account)
            data = {
                "token": token.key,
                "fullname": user_serializer.data['fullname'],
                "email": user_serializer.data['email'],
                "user_id": user_serializer.data['id']
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
