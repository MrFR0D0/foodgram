from users.serializers import (
    CustomUserSerializer, UserAvatarSerializer,
    FollowSerializer, FollowShowSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from djoser.views import UserViewSet
from api.permissions import AnonimOrAuthenticatedReadOnly
from recipes.models import Tag
from api.serializers import TagSerializer
from django.shortcuts import get_object_or_404
from users.models import Follow
from rest_framework.pagination import LimitOffsetPagination

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AnonimOrAuthenticatedReadOnly,)

    @action(
        detail=False, methods=['get', 'patch'], url_path='me',
        url_name='me', permission_classes=(IsAuthenticated,)
    )
    def get_me(self, request):
        """Позволяет пользователю получить подробную информацию о себе
        и редактировать её."""
        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        url_name='subscribe', permission_classes=(IsAuthenticated,)
    )
    def get_subscribe(self, request, id):
        """Позволяет текущему пользователю подписываться/отписываться от
        автора контента, чей профиль он просматривает."""
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'user': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = FollowShowSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )

        try:
            user = Follow.objects.get(user=request.user, author=author)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)














    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        url_name='subscriptions', permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """Возвращает авторов контента, на которых подписан
        текущий пользователь."""

        authors = User.objects.filter(followed__user=request.user)
        paginator = LimitOffsetPagination()
        result_pages = paginator.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = FollowShowSerializer(
            result_pages, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'update_avatar':
            return UserAvatarSerializer
        return super().get_serializer_class()

    @action(
        detail=False, methods=['put', 'delete'],
        url_path='me/avatar', permission_classes=(IsAuthenticated,)
    )
    def update_avatar(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=False
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
