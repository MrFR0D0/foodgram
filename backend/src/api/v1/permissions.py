from rest_framework import permissions


class AnonimOrAuthenticatedReadOnly(permissions.BasePermission):
    """Кастомный пермишен.

    Разрешает анонимному или авторизованному пользователю
    только безопасные запросы.
    """

    def has_object_permission(self, request, view, obj):
        """Переопределение логики доступа."""
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_anonymous or request.user.is_authenticated:
                return True
        return request.user.is_superuser or request.user.is_staff


class AuthorOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен.

    Предоставляет права на осуществление опасных методов запроса
    только автору объекта, в остальных случаях
    доступ запрещен.
    """

    def has_object_permission(self, request, view, object):
        """Переопределение логики доступа."""
        return (
            request.method in permissions.SAFE_METHODS
            or object.author == request.user
        )
