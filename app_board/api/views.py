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
# Board model representing the core entity
from app_board.models import Board
# Custom permission classes for access control
from .permissions import IsBoardMemberOrOwner, IsBoardOwner, IsMemberOrOwnerOfAnyBoard
# Serializers for Board data validation and representation
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateRequestSerializer, BoardUpdateResponseSerializer


class BoardViewSet(viewsets.ModelViewSet):
    """
    Manage boards including listing, creation, retrieval, partial update, and deletion.

    Permissions:
        - create: authenticated users.
        - list: authenticated users who are members/owners of any board.
        - retrieve, partial_update: authenticated users who are members/owners of specific board.
        - destroy: only the owner can delete a board.

    HTTP methods allowed:
        - GET (list and retrieve)
        - POST (create)
        - PATCH (partial_update)
        - DELETE (destroy)

    GET:
        Returns a list or detail of boards accessible to the user.

    POST:
        Creates a new board with the request user as owner.
        Accepts members as list of user IDs.

    PATCH:
        Partially updates board title and members.
        Input serializer expects member IDs.
        Response serializer returns nested owner and members details.

    DELETE:
        Deletes a board, only allowed for owners.

    Notes:
        - The `get_object` method fetches boards differently depending on action to support proper permission checks.
        - Members are explicitly set on create and update to ensure integrity.
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
        Retrieve a Board instance applying queryset restrictions and permission checks.

        For 'destroy', fetch from all boards to enable correct 403 errors.
        Raises 404 if not found.

        Returns:
            Board instance.
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
        Return serializer class depending on action.

        Returns:
            BoardDetailSerializer for retrieve, update actions.
            BoardSerializer otherwise.
        """
        if self.action in ['retrieve', 'update', 'partial_update']:
            return BoardDetailSerializer
        return BoardSerializer

    def perform_create(self, serializer):
        """
        Create and save a new Board with owner and members.

        Args:
            serializer: Serializer with validated data.
        """
        board = serializer.save(owner=self.request.user)
        members = serializer.validated_data.get("members", [])
        board.members.set(members)
        board.save()

    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests to partially update the board.

        Uses separate serializers for input validation and output representation.

        Input:
            members as list of user IDs.
            
        Output:
            Nested owner and members details.

        Returns:
            Response with updated board data.
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
        Return appropriate permissions based on current action.

        Returns:
            List of permission instances.
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
    Validate existence and format of a user email.

    Permissions:
        - Authenticated users only.

    GET:
        Query param 'email' is required.
        Returns user ID, email, and fullname if user exists.
        Returns 400 if no email provided or invalid format.
        Returns 404 if email does not exist.
    """

    permission_classes = [IsAuthenticated]

    def validate_email(self, email):
        """
        Validate the email format.

        Args:
            email (str): Email address to validate.

        Returns:
            bool or Response: True if valid, or HTTP 400 Response if invalid.
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return Response({'error': 'E-mail not valid.'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Handle GET request to check if an email exists in the system.

        Query params:
            email (str): Email address.

        Returns:
            JSON with user info or error message.
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