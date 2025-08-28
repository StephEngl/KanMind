from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q

from app_board.models import Board
from .permissions import IsBoardMemberOrOwner, IsBoardOwner, IsMemberOrOwnerOfAnyBoard
from .serializers import BoardSerializer, BoardDetailSerializer

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound


class BoardViewSet(viewsets.ModelViewSet):
    """
    Handles listing, creating, retrieving, updating, and deleting Boards.
    Permissions vary per action.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return boards where the user is owner or member."""
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
    def get_object(self):
        """
        For 'destroy', allow looking up any Board so that
        403 Forbidden can be raised if user is not owner.
        For other actions, restrict queryset.
        """
        if self.action in ['retrieve', 'update', 'partial_update','destroy']:
            queryset = Board.objects.all()
        else:
            queryset = self.get_queryset()

        try:
            obj = queryset.get(pk=self.kwargs.get(self.lookup_field))
        except Board.DoesNotExist:
            raise NotFound("Board not found")

        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer_class(self):
        """Choose serializer class based on action."""
        if self.action in ['retrieve', 'update', 'partial_update']:
            return BoardDetailSerializer
        return BoardSerializer

    def perform_create(self, serializer):
        """
        Save new board with request user as owner.
        Ensure owner is a member as well, if wished.
        """
        board = serializer.save(owner=self.request.user)
        members = serializer.validated_data.get("members", [])
        board.members.set(members)
        board.save()

    def update(self, request, *args, **kwargs):
        """
        Restrict update to only 'title' and 'members'.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Only accept title and members in updated data
        allowed_fields = {'title', 'members'}
        filtered_data = {key: value for key, value in request.data.items() if key in allowed_fields}

        serializer = self.get_serializer(instance, data=filtered_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        - create: authenticated user
        - list: authenticated + member/owner of any board
        - retrieve, update, partial_update: member or owner of that board
        - destroy: only board owner
        """
        permissions_list = super().get_permissions()
        if self.action == "list":
            permissions_list.append(IsMemberOrOwnerOfAnyBoard())
        elif self.action in ["retrieve", "update", "partial_update"]:
            permissions_list.append(IsBoardMemberOrOwner())
        elif self.action == "destroy":
            permissions_list.append(IsBoardOwner())

        return permissions_list


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