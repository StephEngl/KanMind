"""
View and ViewSet implementations for task and comment management.

Provides:
- TaskViewSet: CRUD operations on tasks with permissions enforcing board membership and ownership.
- AssignedTaskListView: Lists tasks assigned to the current authenticated user.
- ReviewingTaskListView: Lists tasks currently under review by the user.
- CommentViewSet: CRUD for comments with permissions based on board membership and comment ownership.

Permissions:
- Uses custom permissions for board membership, task ownership, and comment authorship.
"""

# 1. Standard library
from app_task.models import Task, Comment

# 2. Third-party
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

# 3. Local imports
from .permissions import IsBoardMemberForTask, IsBoardOwnerOrTaskCreator, IsCommentCreator, IsBoardMemberForComment
from .serializers import TaskSerializer, CommentSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for the Task model.

    Actions:
    - create: Validate board membership and assign creator.
    - partial_update: Permission checked for board membership.
    - destroy: Restricted to board owner or task creator.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'partial_update', 'delete']

    def get_permissions(self):
        """
        Assigns permissions dynamically based on action:
        - IsBoardMemberForTask for create and partial_update.
        - IsBoardOwnerOrTaskCreator for destroy.
        """
        permissions_list = super().get_permissions()
        if self.action in ['create', "partial_update"]:
            permissions_list.append(IsBoardMemberForTask())
        elif self.action == "destroy":
            permissions_list.append(IsBoardOwnerOrTaskCreator())

        return permissions_list
    
    def perform_create(self, serializer):
        """
        Sets the current user as the creator of a new task.
        """
        serializer.save(created_by=self.request.user)


class AssignedTaskListView(generics.ListAPIView):
    """
    Lists tasks where the current user is the assignee.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Returns queryset filtered by current user as assignee.
        """
        user = self.request.user
        tasks = Task.objects.filter(assignee=user)
        return tasks


class ReviewingTaskListView(generics.ListAPIView):
    """
    Lists tasks where the current user is the reviewer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Returns queryset filtered by current user as reviewer.
        """
        user = self.request.user
        tasks = Task.objects.filter(reviewer=user)
        return tasks


class CommentViewSet(viewsets.ModelViewSet):
    """
    Manages comment CRUD operations scoped to a task.

    Permissions:
    - List and create actions require membership in the associated board.
    - Destroy action requires comment creator permission.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """
        Returns comments filtered by task based on URL param task_pk.
        """
        task_id = self.kwargs['task_pk']
        return Comment.objects.filter(task_id=task_id)
    
    def get_permissions(self):
        """
        Append board membership and comment creator permissions based on action.
        """
        permissions_list = super().get_permissions()
        if self.action in ['list', 'create']:
            permissions_list.append(IsBoardMemberForComment())
        if self.action == "destroy":
            permissions_list.append(IsCommentCreator())
        return permissions_list
    
    def get_task(self):
        """
        Utility to retrieve related task from URL parameters.
        """
        task_id = self.kwargs.get('task_pk')
        if not task_id:
            return None
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return None
        
    def perform_create(self, serializer):
        """
        Saves a new comment assigned to the specified task and current user as author.
        """
        task = self.get_task()
        serializer.save(task=task, author=self.request.user)