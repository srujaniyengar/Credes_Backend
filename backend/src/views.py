from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
#mymodules
from .models import Task, Comment, User
from .serializers import (
    RegisterSerializer, TaskSerializer, CommentSerializer, UserListSerializer, MyTokenObtainPairSerializer
)
from .permissions import IsAdmin, IsActiveUser, IsAdminOrAssignedToForTask


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def create(self, request, *args, **kwargs):
        if request.user.role != 'Admin':
            raise PermissionDenied("Only admins can create tasks.")
        return super().create(request, *args, **kwargs)

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsActiveUser, IsAdminOrAssignedToForTask]

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'Admin':
            raise PermissionDenied("Only admins can delete tasks.")
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        if user.role == "Admin":
            return super().update(request, *args, **kwargs)
        if set(request.data.keys()) <= {"status"} and task.assigned_to == user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Only admin or assigned user (for status) can update task.")

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        task = Task.objects.get(pk=self.kwargs['task_id'])
        user = self.request.user
        if user.role == "Admin":
            return Comment.objects.filter(task=task)
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

class UserSoftDeleteView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User not found.")
        if not user.is_active:
            return Response({"detail": "User already inactive."}, status=status.HTTP_400_BAD_REQUEST)
        if user == request.user:
            raise PermissionDenied("You cannot soft-delete yourself.")
        user.is_active = False
        user.save()
        serializer = UserListSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)