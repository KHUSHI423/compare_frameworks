from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # For Board: check owner_id
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        # For Task: check board owner
        if hasattr(obj, 'board'):
            return obj.board.owner == request.user
        return False