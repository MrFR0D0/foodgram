from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import Http404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.v1.permissions import AnonimOrAuthenticatedReadOnly
from api.v1.users.serializers import (
    CustomUserSerializer,
    FollowSerializer,
    FollowShowSerializer,
    UserAvatarSerializer,
)
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AnonimOrAuthenticatedReadOnly,)

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        url_name="me",
        permission_classes=(IsAuthenticated,),
    )
    def get_me(self, request):
        """Метод для пользовател.

        Позволяет пользователю получить подробную информацию о себе
        и редактировать её.
        """
        if request.method == "PATCH":
            serializer = CustomUserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=(IsAuthenticated,),
    )
    def get_subscribe(self, request, id):
        """Метод для подписчика.

        Позволяет текущему пользователю подписываться/отписываться от
        автора контента, чей профиль он просматривает.
        """
        try:
            author = User.objects.annotate(recipes_count=Count("recipes")).get(
                id=id
            )
        except User.DoesNotExist:
            # Если автор не найден:
            if request.method == "DELETE":
                # Для DELETE запроса возвращаем кастомную ошибку
                return Response(
                    {
                        "error": "Невозможно удалить подписку \
                            на несуществующего автора."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Для других методов (например, POST),
            # повторно выбрасываем Http404.
            # DRF перехватит его и вернет стандартное сообщение
            # "No User matches the given query."
            raise Http404() from None

        if request.method == "POST":
            serializer = FollowSerializer(
                data={"user": request.user.id, "author": author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = FollowShowSerializer(
                author, context={"request": request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        deleted_count, _ = Follow.objects.filter(
            user=request.user, author__id=id
        ).delete()
        if deleted_count == 0:
            return Response(
                {"error": "Невозможно удалить несуществующую подписку"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(IsAuthenticated,),
    )
    def get_subscriptions(self, request):
        """Метод для подписчика.

        Возвращает авторов контента, на которых подписан
        текущий пользователь.
        """
        authors = User.objects.filter(followed__user=request.user).annotate(
            recipes_count=Count("recipes")
        )
        paginator = LimitOffsetPagination()
        result_pages = paginator.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = FollowShowSerializer(
            result_pages, context={"request": request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        """Определение сериализатора."""
        if self.action == "update_avatar":
            return UserAvatarSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=["put", "delete"],
        url_path="me/avatar",
        permission_classes=(IsAuthenticated,),
    )
    def update_avatar(self, request, *args, **kwargs):
        """Обновление аватара."""
        user = self.request.user
        if request.method == "PUT":
            serializer = self.get_serializer(
                user, data=request.data, partial=False
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def profile(self, request, pk=None):
        """Получение профиля пользоватеоя."""
        user = self.get_object()
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
