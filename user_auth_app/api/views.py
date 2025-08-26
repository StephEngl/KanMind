from user_auth_app.models import UserProfile

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # serializer = RegistrationSerializer(data=request.data)
        # if serializer.is_valid():
        #     user = serializer.save()
        #     token = Token.objects.create(user=user)
        #     return Response({
        #         "user": UserProfileSerializer(user).data,
        #         "token": token.key
        #     }, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pass