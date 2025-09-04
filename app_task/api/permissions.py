"""
Custom permission classes for task and comment access control in board context.

Permissions:
- IsBoardMemberForTask: Allows access only for members of related board, especially on task creation.
- IsBoardMemberForComment: Allows access only for members of the board related to a comment's task.
- IsBoardOwnerOrTaskCreator: Allows modifications only by board owner or task creator.
- IsCommentCreator: Allows comment deletion only by the comment's creator.
"""

# 2. Third-party
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.exceptions import NotFound, ValidationError

# 3. Local imports
from app_board.models import Board


class IsBoardMemberForTask(BasePermission):
    """
    Permission: Allows action only if user is a member of the specified board.

    Checks board existence on create.
    """
    message = "You must be a member of this board."

    def has_permission(self, request, view):
        if view.action == 'create':
            board_id = request.data.get("board")
            if not board_id:
                raise ValidationError({"board": "Board must be specified."})
            try:
                board = Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                raise NotFound(detail="Board does not exist.")
            return request.user in board.members.all()
        return True
    
    def has_object_permission(self, request, view, obj):
        return request.user in obj.board.members.all()


class IsBoardMemberForComment(BasePermission):
    """
    Permission: Allows access only for members of the board associated with the comment's task.
    """
    message = "You must be a member of this board."
    
    def has_permission(self, request, view):
        task = view.get_task()
        if not task:
            raise NotFound({"task": "Task does not exist."})
        board = task.board
        return request.user in board.members.all()


class IsBoardOwnerOrTaskCreator(BasePermission):
    """
    Permission: Allows access only to board owner or creator of related task.
    """
    message = "You must be the board owner or the creator of this task."

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_board_owner = (obj.board.owner == user)
        is_task_creator = (obj.created_by is not None and obj.created_by == user)
        return is_board_owner or is_task_creator


class IsCommentCreator(BasePermission):
    """
    Permission: Allows deletion only for creator of a comment.
    """
    message = "You must be the creator of this comment."

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_comment_creator = (obj.author is not None and obj.author == user)
        return is_comment_creator
