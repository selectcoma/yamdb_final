from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """Read only for unauthenticated users"""

    def has_permission(self, request, view):
        return (
            request.method in
            permissions.SAFE_METHODS or request.user.is_authenticated
        )


class IsAuthor(permissions.BasePermission):
    """Checks if user == author"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author


class IsModerator(permissions.BasePermission):
    """Checks if user == moderator"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'moderator'
        )


class IsAdmin(permissions.BasePermission):
    """Checks if user == admin"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'admin'
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Checks if user is admin and if not gives only read access"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.role == 'admin'
            or request.user.is_superuser
        )


class AuthorOrReadOnlyPermission(permissions.BasePermission):
    """Checks if user is the author of the object,
     moderator or admin"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in
            permissions.SAFE_METHODS or obj.author
            == request.user or request.user.role in ['admin', 'moderator']
        )
