from django.contrib.auth.models import User

from rest_framework import serializers

from app_auth.api.serializers import UserInfoSerializer
from app_board.models import Board
from app_task.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task data representation and validation.

    Fields:
        - assignee (UserInfoSerializer, read-only): Information about the user assigned to the task.
        - reviewer (UserInfoSerializer, read-only): Information about the user reviewing the task.
        - comments_count (int, read-only): Number of comments on the task.
    """
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority',
                'assignee', 'reviewer', 'due_date', 'comments_count']
    

class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

        def update(self, instance, validated_data):
            assignee_data = validated_data.pop('assignee', None)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            if assignee_data:
                assignee = User.objects.get(**assignee_data)
                instance.assignee = assignee
            instance.save()
            return instance
