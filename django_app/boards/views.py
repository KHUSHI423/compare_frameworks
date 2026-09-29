from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Attachment, Board, Task
from .serializers import BoardSerializer, TaskSerializer
from .permissions import IsOwner
import csv
import os
from django.conf import settings
from django.http import HttpResponse

class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return Board.objects.filter(owner=self.request.user)
        return Board.objects.all()

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied("Not authorized to access this board")
        return obj

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def attachment(self, request, pk=None):
        board = self.get_object()
        file = request.FILES.get('file')
        
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        safe_name = f"{pk}_{file.name}"
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        path = os.path.join(settings.MEDIA_ROOT, safe_name)
        
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        Attachment.objects.create(
            board=board,
            file_path=path,
            original_filename=file.name
        )
        
        return Response({"url": f"/uploads/{safe_name}", "filename": file.name})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def export(self, request, pk=None):
        board = self.get_object()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="board_{pk}_tasks.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['id', 'title', 'status', 'due_date', 'created_at'])
        
        for task in Task.objects.filter(board=board).iterator():
            writer.writerow([task.id, task.title, task.status, task.due_date, task.created_at])
        return response

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        board_id = self.kwargs.get('board_id')
        qs = Task.objects.filter(board_id=board_id, board__owner=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs
    
    def perform_create(self, serializer):
        board_id = self.kwargs.get('board_id')
        board = Board.objects.filter(id=board_id, owner=self.request.user).first()
        if not board:
            raise NotFound("Board not found or not owned")
        serializer.save(board=board)