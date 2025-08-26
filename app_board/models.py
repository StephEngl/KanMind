from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return self.title