from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsModerator(BasePermission):
    """Moderator can only manage resources belonging to users in the same group."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "moderator")

    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        return self._same_group(request.user.group_id, obj)

    @staticmethod
    def _same_group(moderator_group_id, obj):
        if moderator_group_id is None:
            return False
        page_group_id = None
        if hasattr(obj, "group_id"):
            page_group_id = obj.group_id
        elif hasattr(obj, "page"):
            page_group_id = obj.page.group_id
        return page_group_id is not None and moderator_group_id == page_group_id


class IsPageOwner(BasePermission):
    """Works for both Page objects (obj.user_id) and Post objects (obj.page.user_id)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user_id = str(request.user.id)
        if hasattr(obj, "user_id"):
            return str(obj.user_id) == user_id
        if hasattr(obj, "page"):
            return str(obj.page.user_id) == user_id
        return False
