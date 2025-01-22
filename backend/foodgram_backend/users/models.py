from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_backend import constants
from users.validators import username_validator


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOICES = (
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Админ'),
    )
    username = models.CharField(
        verbose_name='Никнейм',
        max_length=constants.MAX_USERNAME_LENGHT,
        unique=True,
        validators=[username_validator],
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text='Введите свое имя'
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Введите свою фамилию',
        max_length=150
    )

    role = models.CharField(
        max_length=constants.MAX_ROLE_LENGHT,
        choices=CHOICES,
        default=USER,
        verbose_name='Уровень доступа пользователя',
        help_text='Уровень доступа пользователя'
    )

    bio = models.TextField(
        max_length=constants.MAX_BIO_LENGHT,
        blank=True,
        verbose_name='Заметка о пользователе',
        help_text='Напишите заметку о себе'
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта пользователя',
        help_text='Введите свой электронный адрес'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff
