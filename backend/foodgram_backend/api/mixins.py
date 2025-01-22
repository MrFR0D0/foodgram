from rest_framework import filters, status
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.permissions import IsAdminUserOrReadOnly


class ModelMixinSet(CreateModelMixin, ListModelMixin,
                    DestroyModelMixin, GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)


class UpdateMixin:
    def update(self, request, *args, **kwargs):
        """Отключает метод PUT, поддерживается только PATCH."""
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
