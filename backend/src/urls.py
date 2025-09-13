from django.urls import path
from .views import (
    RegisterView, TaskListCreateView, TaskRetrieveUpdateDestroyView,
    CommentListCreateView, UserListView, UserSoftDeleteView, MyTokenObtainPairView
)
def api_root(request):
    return JsonResponse({"message": "Welcome to the Credes API!"})
urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/soft-delete/', UserSoftDeleteView.as_view(), name='user-soft-delete'),
]