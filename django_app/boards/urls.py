from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

# Nested tasks route
task_router = DefaultRouter()
task_router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('boards/<int:board_id>/', include(task_router.urls)),
]