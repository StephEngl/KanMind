"""
Imports for Board views and related functionality.

Conventions:
- 1. Standard library imports for core Python modules.
- 2. Third-party imports for Django and Django REST Framework utilities.
- 3. Local application imports for models, permissions, and serializers.
"""
# 1. Standard Library Imports
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.db.models import Q

# 2. Third-party
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

# 3. Local imports
from app_board.models import Board
from .permissions import IsBoardMemberOrOwner, IsBoardOwner, IsMemberOrOwnerOfAnyBoard
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateRequestSerializer, BoardUpdateResponseSerializer


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for boards: list, create, retrieve, update, and delete.

    - create: Authenticated users only.
    - list: Authenticated users (member/owner of any board).
    - retrieve/partial_update: Member or owner of board.
    - destroy: Owner only.
    - Handles integrity on member setting (create/update).
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """
        Get boards where the request user is owner or member.
        Returns: 
            QuerySet: Boards filtered for the requesting user.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
    def get_object(self):
        """
        Gets a board for detail/update/delete actions with full permission checking.

        Raises:
            NotFound: if board does not exist.
        """
        if self.action in ['retrieve', 'partial_update','destroy']:
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
        """
        Returns serializer class based on action.
        """
        if self.action in ['retrieve', 'update', 'partial_update']:
            return BoardDetailSerializer
        return BoardSerializer

    def perform_create(self, serializer):
        """
        Saves a new board, assigning the owner and setting members.
        """
        board = serializer.save(owner=self.request.user)
        members = serializer.validated_data.get("members", [])
        board.members.set(members)
        board.save()

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates board members/title, returns nested response.
        """
        instance = self.get_object()
        req_serializer = BoardUpdateRequestSerializer(instance, data=request.data, partial=True)
        req_serializer.is_valid(raise_exception=True)
        board = req_serializer.save()

        members = req_serializer.validated_data.get('members', [])
        board.members.set(members)
        board.save()

        # Return updated board with nested members and owner
        res_serializer = BoardUpdateResponseSerializer(board)
        return Response(res_serializer.data)

    def get_permissions(self):
        """
        Appends action-specific board permission classes.
        """
        permissions_list = super().get_permissions()
        if self.action == "list":
            permissions_list.append(IsMemberOrOwnerOfAnyBoard())
        elif self.action in ["retrieve", "partial_update"]:
            permissions_list.append(IsBoardMemberOrOwner())
        elif self.action == "destroy":
            permissions_list.append(IsBoardOwner())

        return permissions_list


class EmailCheckView(APIView):
    """
    APIView for validating email existence and format.

    - GET with 'email' param required.
    - Returns 200 with user info if found.
    - Returns 400 on format/user missing.
    - Returns 404 if email does not exist in system.
    """

    permission_classes = [IsAuthenticated]

    def validate_email(self, email):
        """
        Validates email format, returns True or 400 Response.
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return Response({'error': 'E-mail not valid.'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Handles GET to check if email exists; returns minimal user info or error.
        """
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