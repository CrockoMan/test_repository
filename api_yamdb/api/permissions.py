from rest_framework import permissions


class IsAdmin(permissions.IsAdminUser):
    """Права для работы с пользователями."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrModeratorOrAdminOrReadOnly(
    permissions.IsAuthenticatedOrReadOnly
):
    """Права для работы с отзывами и комментариями."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права для работы с категориями и жанрами."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    """Обеспечивает доступ админу."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_admin or request.user.is_superuser)
        return request.method in permissions.SAFE_METHODS


class IsAuthorModeratorAdminOrReadOnlyPermission(permissions.BasePermission):
    """Автору, модератор админ."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user or request.user.is_moderator
                or request.user.is_admin or request.user.is_superuser)


class IsAdminOnlyPermission(permissions.BasePermission):
    """Только aдмин."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_admin or request.user.is_superuser)
        return False
