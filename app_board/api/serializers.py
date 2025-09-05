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
from rest_framework import serializers

# 3. Local imports
from app_auth.api.serializers import UserInfoSerializer
from app_task.api.serializers import BoardTaskSerializer
from app_board.models import Board


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializes Board instances with aggregation and member management.

    - members: Write-only user ID list.
    - Aggregates member/task counts, owner ID (read-only).
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
