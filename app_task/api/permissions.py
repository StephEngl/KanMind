from rest_framework.permissions import SAFE_METHODS, BasePermission

from app_board.models import Board


class IsBoardMember(BasePermission):
    """
    Allow access only to members of the board.
    """

    message = "You must be a member of this board."

    def has_permission(self, request, view):
        if request.method == "POST":
            board_id = request.data.get("board")
            if not board_id:
                self.message = "Board must be specified."
                return False
            try:
                board = Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                self.message = "Board does not exist."
                return False
            return request.user in board.members.all()
        return True


class IsBoardOwnerOrTaskCreator(BasePermission):
    """
    Custom permission allowing access only if user is the owner of the board
    related to the task or creator of the task.
    """
    message = "You must be the board owner or the creator of this task."

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_board_owner = (obj.board.owner == user)
        is_task_creator = (obj.created_by is not None and obj.created_by == user)
        return is_board_owner or is_task_creator


class IsCommentCreator(BasePermission):
    """
    Custom permission to only allow the creator of a comment to access it.
    """
    message = "You must be the creator of this comment."
    pass
