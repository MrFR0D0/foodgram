from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

import constants
from recipes.models import Recipe
from recipes.utils import Base64ImageField
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта класса User."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"max_length": constants.MAX_USERNAME_LENGHT},
        }

    def validate_username(self, value):
        """Проверка корректности мени пользователя."""
        validator = RegexValidator(
            regex=constants.USERNAME_CHECK,
            message="Имя пользователя содержит недопустимый символ",
        )
        validator(value)
        if value == constants.NOT_ALLOWED_USERNAME:
            raise serializers.ValidationError("недопустимое имя")
        return value


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return object.follower.filter(user=request.user).exists()


class UserAvatarSerializer(UserSerializer):
    """Сериализатор для модели User."""

    avatar = Base64ImageField(required=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ("avatar",)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""

    class Meta:
        model = Follow
        fields = ("user", "author")
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("author", "user"),
                message="Вы уже подписывались на этого автора",
            )
        ]

    def validate(self, data):
        """Проверяем, что пользователь не подписывается на самого себя."""
        if data["user"] == data["author"]:
            raise serializers.ValidationError(
                "Подписка на cамого себя не имеет смысла"
            )
        return data


class FollowRecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в подписке."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowShowSerializer(CustomUserSerializer):
    """Сериализатор отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_recipes(self, object):
        """Получение рецепта."""
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        author_recipes = object.recipes.all()
        if recipes_limit and recipes_limit.isnumeric():
            recipes_limit = int(recipes_limit)
            author_recipes = author_recipes[:recipes_limit]
        return FollowRecipeShortSerializer(author_recipes, many=True).data
