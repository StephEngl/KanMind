from django.contrib.auth import authenticate, get_user_model
from .serializers import RegistrationSerializer, UserProfileSerializer

from app_auth.models import UserProfile

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User = get_user_model()
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Username für Authentifizierung nehmen
        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            data = {
                "token": token.key,
                "fullname": user.username,
                "email": user.email,
                "user_id": user.id,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer_class = RegistrationSerializer
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                "token": token.key,
                "fullname": saved_account.username,
                "email": saved_account.email,
                "user_id": saved_account.id,
            }
        else:
            data = serializer.errors
        return Response(data, status=status.HTTP_201_CREATED)
