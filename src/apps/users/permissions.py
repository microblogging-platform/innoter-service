from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return str(obj.user_id) == str(request.user.id)