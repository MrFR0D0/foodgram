from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
import base64
from users.validators import username_validator
from django.core.validators import RegexValidator
from users.models import Follow
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import Recipe
from foodgram_backend.utilits import Base64ImageField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта класса User."""
    username = serializers.CharField(
        max_length=150,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        return username_validator(value)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.follower.filter(user=request.user).exists()


class UserAvatarSerializer(UserSerializer):
    """Сериализатор для модели User."""

    avatar = Base64ImageField(
        required=False,
        # allow_null=True
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'avatar',
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписывались на этого автора'
            )
        ]

    def validate(self, data):
        """Проверяем, что пользователь не подписывается на самого себя."""
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Подписка на cамого себя не имеет смысла'
            )
        return data


class FollowRecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в подписке."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowShowSerializer(CustomUserSerializer):
    """Сериализатор отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, object):
        author_recipes = object.recipes.all()[:10]
        return FollowRecipeShortSerializer(
            author_recipes, many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()
