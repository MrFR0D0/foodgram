from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from users.validators import username_validator

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
            'password'
        )
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        return username_validator(value)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    # is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            # 'last_name',
            # 'is_subscribed'
        )
