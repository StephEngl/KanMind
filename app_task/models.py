"""
Module defining Task and Comment models for board-related task management.

Contains:
- Task: Represents tasks on a board with status, priority, and user relations.
- Comment: Represents comments on tasks with author and timestamps.
"""

# 1. Standard library
from django.db import models
from django.contrib.auth.models import User

# 3. Local imports
from app_board.models import Board


STATUS_CHOICES = [
    ('to-do', 'To Do'),
    ('in-progress', 'In Progress'),
    ('review', 'Review'),
    ('done', 'Done'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

class Task(models.Model):
    """
    Model representing a task within a board.

    Attributes:
        board (ForeignKey): Related board instance.
        title (CharField): Title of the task.
        description (TextField): Optional, detailed description.
        status (CharField): Task status, limited to STATUS_CHOICES.
        priority (CharField): Task priority, limited to PRIORITY_CHOICES.
        assignee (ForeignKey): User assigned to work on task, nullable.
        reviewer (ForeignKey): User reviewing the task, nullable.
        due_date (DateField): Optional deadline.
        created_by (ForeignKey): User who created the task, nullable.
        created_at (DateTimeField): Timestamp of creation.
        updated_at (DateTimeField): Timestamp of last update.

    Methods:
        __str__: Returns task title as string representation.
    """
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assignee = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(User, related_name='review_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='created_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Model representing a comment posted on a task.

    Attributes:
        task (ForeignKey): Related task instance.
        author (ForeignKey): User who authored this comment.
        content (TextField): The comment text.
        created_at (DateTimeField): Timestamp of comment creation.

    Meta:
        ordering: Returns comments in chronological order by creation date.

    Methods:
        __str__: Returns string representation identifying author and task.
    """
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.task.title}'