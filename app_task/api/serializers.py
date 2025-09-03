from django.contrib.auth.models import User

from rest_framework import serializers

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

    # Input fields for IDs of assignee and reviewer with validation against User table
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

    # Output fields for nested user info
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
            dict: The validated attrs.

        Raises:
            serializers.ValidationError: If validations fail.
        """
        # Get the board instance either from input (create) or existing instance (update)
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


class BoardTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'assignee', 'reviewer',
            'due_date', 'comments_count'
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip()