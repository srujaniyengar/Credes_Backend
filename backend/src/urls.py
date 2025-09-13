from django.urls import path
from django.http import JsonResponse  # <-- Add this import
from .views import (
    RegisterView, TaskListCreateView, TaskRetrieveUpdateDestroyView,
    CommentListCreateView, UserListView, UserSoftDeleteView, MyTokenObtainPairView
)

def api_root(request):
    return JsonResponse({
        "message": "Welcome to the Credes API!",
        "endpoints": {
            "/auth/register/": "POST - Register a new user",
            "/auth/login/": "POST - Obtain JWT token (login)",
            "/tasks/": "GET, POST - List all tasks or create a new task",
            "/tasks/<pk>/": "GET, PUT, PATCH, DELETE - Retrieve, update, or delete a specific task",
            "/tasks/<task_id>/comments/": "GET, POST - List or add comments for a task",
            "/users/": "GET - List all users",
            "/users/<pk>/soft-delete/": "POST - Soft delete a user"
        }
    })

urlpatterns = [
    path('', api_root),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/soft-delete/', UserSoftDeleteView.as_view(), name='user-soft-delete'),
]