from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin' and request.user.is_active

class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

class IsAdminOrAssignedToForTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or not user.is_active:
            return False
        if user.role == 'Admin':
            return True
        # SAFE_METHODS means GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS and obj.assigned_to == user:
            return True
        # Allow PATCH only if patching "status" and user is assignee
        if request.method == "PATCH" and obj.assigned_to == user:
            data = request.data
            # If status is the only field being updated
            return set(data.keys()) <= {"status"}
        return False