# django_app/boards/models.py
from django.db import models
from django.conf import settings
import uuid
import os

class Board(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='boards'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "boards"

    def __str__(self):
        return self.title

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo', 'Todo'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.TODO
    )
    board = models.ForeignKey(
        Board, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tasks"

    def __str__(self):
        return self.title

class Attachment(models.Model):
    id = models.AutoField(primary_key=True)
    board = models.ForeignKey(
        Board, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file_path = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attachments"