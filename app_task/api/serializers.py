from django.contrib.auth.models import User

from app_board.models import Board
from app_task.models import Task

from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def create(self, validated_data):
        assignee_data = validated_data.pop('assignee', None)
        task = Task.objects.create(**validated_data)
        if assignee_data:
            assignee = User.objects.get(**assignee_data)
            task.assignee = assignee
        task.save()
        return task
    

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
