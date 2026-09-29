from rest_framework import serializers
from .models import Board, Task

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'created_at']
        read_only_fields = ['owner_id', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'board_id', 'due_date', 'created_at']
        read_only_fields = ['board_id', 'created_at']