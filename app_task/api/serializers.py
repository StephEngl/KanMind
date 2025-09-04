"""
Serializers module for task management API.

Includes serializers for Tasks and Comments with nested user info and validation logic.

Features:
- TaskSerializer: Handles task creation, update, and validation of board membership.
- BoardTaskSerializer: Simplified task serializer excluding board relation.
- CommentSerializer: Handles comment representation with author info.
"""

# 1. Standard library
from django.contrib.auth.models import User

# 2. Third-party
from rest_framework import serializers

# 3. Local imports
from app_auth.api.serializers import UserInfoSerializer
from app_board.models import Board
from app_task.models import Task, Comment


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task representation and validation.

    Handles:
    - Writing assignee_id and reviewer_id as user PKs on create/update.
    - Reading nested detailed info for assignee and reviewer in API responses.
    - Read-only comments count.

    Validates:
    - That assignee and reviewer (if given) are members of the associated board.
    - That a board must always be specified and exist.
    """

    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority',
                'assignee_id', 'reviewer_id', 'assignee', 'reviewer', 'due_date', 
                'comments_count']

    def get_comments_count(self, obj):
        """
        Returns the count of comments related to this task.
        """
        return obj.comments.count()
    
    def validate(self, attrs):
        """
        Validates that assignee and reviewer (if provided) are members of the board.
        Also ensures the board is specified and exists.

        Args:
            attrs (dict): Validated field data before final save.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If the validations fail.
        """
        board = attrs.get('board') or getattr(self.instance, 'board', None)
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        
        if assignee and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError({
                'assignee_id': 'Assignee must be a member of the board.'
            })
        if reviewer and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError({
                'reviewer_id': 'Reviewer must be a member of the board.'
            })

        return attrs

class TaskPartialUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority',
                'assignee_id', 'reviewer_id', 'assignee', 'reviewer', 'due_date']


class BoardTaskSerializer(TaskSerializer):
    """
    Serializer variant for Task model tailored for board-level views.

    Inherits all validation and field handling from TaskSerializer.

    Fields:
        - id: Task identifier.
        - title: Title of the task.
        - description: Detailed description.
        - status: Current task status.
        - priority: Task priority level.
        - assignee_id: ID of the user assigned to the task (write-only).
        - reviewer_id: ID of the user reviewing the task (write-only).
        - assignee: Nested user info for assignee (read-only).
        - reviewer: Nested user info for reviewer (read-only).
        - due_date: Deadline date.
        - comments_count: Number of comments associated with the task (read-only).
    """
    class Meta(TaskSerializer.Meta):
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'assignee', 'reviewer',
            'due_date', 'comments_count'
        ]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model instances.

    Provides serialized fields for displaying comment metadata and content.

    Fields:
        - id: Unique identifier of the comment (read-only).
        - created_at: Timestamp when the comment was created (read-only).
        - author: Full name of the comment's author, dynamically constructed (read-only).
        - content: The text content of the comment.

    Methods:
        - get_author(obj): Returns the full name of the author concatenated from first and last names.
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip()