from app_board.models import Board

from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """
    Object-level permission: Allow access only to board owner or members.
    """
    message = "You must be the owner or a member of this board."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()

class IsBoardOwner(BasePermission):
    """
    Object-level permission: Allow delete only to board owner.
    """
    message = "Only the board owner may delete this board."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsMemberOrOwnerOfAnyBoard(BasePermission):
    """
    View-level permission: Allow list only if user is member or owner of any board.
    """
    message = "You are not a member of any board."

    def has_permission(self, request, view):
        return Board.objects.filter(Q(owner=request.user) | Q(members=request.user)).exists()