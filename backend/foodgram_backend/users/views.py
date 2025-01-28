from users.serializers import CustomUserSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from djoser.views import UserViewSet

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для создания обьектов класса User."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = (AnonimOrAuthenticatedReadOnly,)