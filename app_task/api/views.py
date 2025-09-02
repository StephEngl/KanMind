# from xml.etree.ElementTree import Comment
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from app_task.models import Task, Comment
from app_board.models import Board
from .permissions import IsBoardMember, IsBoardOwnerOrTaskCreator, IsCommentCreator
from .serializers import TaskSerializer, CommentSerializer

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle CRUD operations for tasks.

    - Checks if Board exists before attempting to create a Task.
    - Applies permission that user must be board member for creation and other actions.
    """
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        """
        Return appropriate permissions based on current action.
        Enforces IsBoardMember for create, list, retrieve, partial_update.
        Enforces IsCommentCreator for destroy.
        """
        permissions_list = super().get_permissions()
        if self.action in ['create', 'list']:
            permissions_list.append(IsBoardMember())
        elif self.action in ["retrieve", "partial_update"]:
            permissions_list.append(IsBoardMember())
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
        return Task.objects.filter(assignee=user)


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
            permissions_list.append(IsBoardMember())
        if self.action == "destroy":
            permissions_list.append(IsCommentCreator())
        return permissions_list


class CommentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs['pk']
        return Comment.objects.filter(task_id=task_id)


class CommentDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCommentCreator]
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs['pk-comment']
        return Comment.objects.filter(task_id=task_id)
