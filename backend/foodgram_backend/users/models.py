from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import username_validator


class User(AbstractUser):
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Адрес электронной почты',
        help_text='Введите свой адрес электронной почты'
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=150,
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
    # # Тут обманка, надо доделать
    # is_subscribed = models.BooleanField(
    #     verbose_name='Подписан ли текущий пользователь на этого',
    # # Надо как то реализовать проверку, возможно через валидатор
    #     default=True,
    # )
    # avatar = models.CharField(
    #     blank=True,
    #     null=True,
    #     verbose_name='Имя',
    #     max_length=150,
    #     help_text='Введите свое имя'
    # )

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username
