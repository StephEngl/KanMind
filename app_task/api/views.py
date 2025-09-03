from app_task.models import Task, Comment
from .permissions import IsBoardMemberForTask, IsBoardOwnerOrTaskCreator, IsCommentCreator, IsBoardMemberForComment
from .serializers import TaskSerializer, CommentSerializer

from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle CRUD operations for tasks.

    - Checks if Board exists before attempting to create a Task.
    - Applies permission that user must be board member for creation and other actions.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'partial_update', 'delete']

    def get_permissions(self):
        """
        Return appropriate permissions based on current action.
        Enforces IsBoardMember of the task's board for create, list, retrieve, partial_update.
        Enforces IsCommentCreator for destroy.
        """
        permissions_list = super().get_permissions()
        if self.action in ['create', "partial_update"]:
            permissions_list.append(IsBoardMemberForTask())
        elif self.action == "destroy":
            permissions_list.append(IsBoardOwnerOrTaskCreator())

        return permissions_list
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AssignedTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        tasks = Task.objects.filter(assignee=user)
        return tasks


class ReviewingTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        tasks = Task.objects.filter(reviewer=user)
        return tasks


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        task_id = self.kwargs['task_pk']
        return Comment.objects.filter(task_id=task_id)
    
    def get_permissions(self):
        permissions_list = super().get_permissions()
        if self.action in ['list', 'create']:
            permissions_list.append(IsBoardMemberForComment())
        if self.action == "destroy":
            permissions_list.append(IsCommentCreator())
        return permissions_list
    
    def get_task(self):
        task_id = self.kwargs.get('task_pk')
        if not task_id:
            return None
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return None
        
    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(task=task, author=self.request.user)