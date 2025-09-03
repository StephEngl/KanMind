"""
Module defining the Board model representing project boards.

Contains:
- Board: Model representing a board with a title, owner, and members.
"""

# 1. Standard library
from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    """
    Model representing a project board.

    Attributes:
        title (CharField): Title of the board, max length 255 characters.
        owner (ForeignKey): Reference to User model representing the board owner.
            Related name 'owned_boards' for reverse lookup.
        members (ManyToManyField): Many-to-many relation with User model representing board members.
            Related name 'boards' for reverse lookup.

    Methods:
        __str__:
            Returns the board's title as the string representation.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return self.title