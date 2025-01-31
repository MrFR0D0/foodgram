from users.serializers import CustomUserSerializer, UserAvatarSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from djoser.views import UserViewSet
from api.permissions import IsCurrentUserOrAdminOrReadOnly
from api.models import Tag
from api.serializers import TagSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для создания обьектов класса User."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'update_avatar':
            return UserAvatarSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def update_avatar(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def profile(self, request, pk=None):
        user = self.get_object()
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
