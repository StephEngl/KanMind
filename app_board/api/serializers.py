"""
Imports for Board serializers and related models.

Conventions:
- 1. Standard library imports for core Django models.
- 2. Third-party imports for DRF serializers.
- 3. Local imports for project-specific serializers and models.
"""
# 1. Standard library
from django.contrib.auth.models import User

# 2. Third-party
# DRF serializer base classes
from rest_framework import serializers

# 3. Local imports
# Serializer for user info reuse
from app_auth.api.serializers import UserInfoSerializer
# Serializer for task info reuse
from app_task.api.serializers import BoardTaskSerializer
# Board model definition
from app_board.models import Board
# Task model definition
from app_task.models import Task



class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and listing boards with summary counts and write-only members list.

    Fields:
        - members (list[int], write-only): Primary keys of users to add as members.
        - member_count (int, read-only): Number of board members.
        - ticket_count (int, read-only): Number of tasks associated with the board.
        - tasks_to_do_count (int, read-only): Count of tasks with 'to-do' status.
        - tasks_high_prio_count (int, read-only): Count of tasks with 'high' priority.
        - owner_id (int, read-only): ID of the board owner.

    Notes:
        - Members are passed as IDs when writing but not included in serialized output.
        - Aggregated counts are computed dynamically.
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            "members",
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
        ]

    def get_member_count(self, obj):
        """Return the number of members in this board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tasks associated with this board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with 'to-do' status."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of tasks with 'high' priority."""
        return obj.tasks.filter(priority='high').count()


class BoardDetailSerializer(BoardSerializer):
    """
    Serializer for detailed board representation including members and tasks.
    
    Overrides: 
        - members: Expanded member info (UserInfoSerializer, read-only).
        - tasks: Nested task details (BoardTaskSerializer, read-only).
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserInfoSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta(BoardSerializer.Meta):
        fields = ['id', 'title', 'owner_id', 'members'] + ['tasks']


class BoardUpdateRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH/PUT requests: Accepts members by ID.
    
    Fields:
        - members: List of user IDs to be added as members.
        - title (str): Title of the board.
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=True,
        write_only=True
    )

    class Meta:
        model = Board
        fields = ['title', 'members']


class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH/PUT responses: Returns nested member info.

    Fields:
        - owner_data: Information about the board owner (UserInfoSerializer, read-only).
        - members_data: Information about the board members (UserInfoSerializer, read-only).
    """
    owner_data = UserInfoSerializer(source='owner', read_only=True)
    members_data = UserInfoSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
