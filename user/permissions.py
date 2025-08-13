from rest_framework.permissions import BasePermission


class CanEditUserPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            (obj.id == request.user.id or request.user.is_staff or request.user.is_superuser)
        )
