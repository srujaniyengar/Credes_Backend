from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Task, Comment, User
from .serializers import (
    RegisterSerializer, TaskSerializer, CommentSerializer, UserListSerializer
)
from .permissions import IsAdmin, IsAdminOrAssignedToForTask

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            return Task.objects.all()
        # Users see only assigned tasks
        return Task.objects.filter(assigned_to=user)

    def create(self, request, *args, **kwargs):
        if request.user.role != 'Admin':
            raise PermissionDenied("Only admins can create tasks.")
        return super().create(request, *args, **kwargs)

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAssignedToForTask]

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'Admin':
            raise PermissionDenied("Only admins can delete tasks.")
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # PATCH: allow only status update for assigned user, or any update for admin
        task = self.get_object()
        user = request.user
        if user.role == "Admin":
            return super().update(request, *args, **kwargs)
        # Only allow updating "status" field for assigned user
        if set(request.data.keys()) <= {"status"} and task.assigned_to == user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Only admin or assigned user (for status) can update task.")

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task = Task.objects.get(pk=self.kwargs['task_id'])
        user = self.request.user
        if user.role == "Admin":
            return Comment.objects.filter(task=task)
        # User can see comments only for their own tasks
        if task.assigned_to == user:
            return Comment.objects.filter(task=task)
        return Comment.objects.none()

    def perform_create(self, serializer):
        task = Task.objects.get(pk=self.kwargs['task_id'])
        user = self.request.user
        if (task.assigned_to != user) and (user.role != "Admin"):
            raise PermissionDenied("Only the assigned user or an Admin can comment on this task.")
        serializer.save(author=user, task=task)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdmin]