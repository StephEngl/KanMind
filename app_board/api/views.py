from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q

from app_board.models import Board
from .permissions import IsBoardMemberOrOwner
from .serializers import BoardSerializer, BoardDetailSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class BoardListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def get(self, request):
        boards = self.get_queryset()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            board = serializer.save(owner=request.user)
            members = serializer.validated_data.get('members', [])
            board.members.set(members)

            if request.user not in members:
                board.members.add(request.user)

            board.save()
            output_serializer = BoardSerializer(board)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardRetrieveUpdateDestroyView(APIView):
    def get_object(self, pk):
        try:
            return Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return None

    def get(self, request, pk):
        board = self.get_object(pk)
        if board is not None:
            user = request.user
            if user not in board.members.all() and user != board.owner:
                return Response({'error': 'You do not have permission to view this board. You have to be a member or the owner.'}, status=status.HTTP_403_FORBIDDEN)

            serializer = BoardDetailSerializer(board)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        board = self.get_object(pk)
        if board is not None:
            serializer = BoardDetailSerializer(board, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        board = self.get_object(pk)
        if board is not None:
            board.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def validate_email(self, email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return Response({'error': 'E-mail not valid.'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'No e-mail-address found.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            data = {
                "id": user.id,
                "email": user.email,
                "fullname": user.username,
                }
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'E-mail-address does not exist.'}, status=status.HTTP_404_NOT_FOUND)