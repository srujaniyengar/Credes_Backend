from rest_framework import serializers
from .models import User, Task, Comment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            role='User',
            password=validated_data['password']
        )
        return user

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_inactive = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_assigned_to_inactive(self, obj):
        return not obj.assigned_to.is_active if obj.assigned_to else None

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('created_at',)

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'is_active', 'date_joined')

# Custom JWT serializer to block inactive users
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_active:
            raise AuthenticationFailed('User account is inactive (soft deleted).')
        return data