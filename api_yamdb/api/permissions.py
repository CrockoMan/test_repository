from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права для работы с категориями и жанрами."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorModeratorAdminOrReadOnlyPermission(permissions.BasePermission):
    """Автор, модератор админ."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)


class IsAdminOnlyPermission(permissions.BasePermission):
    """Только aдмин."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser))
