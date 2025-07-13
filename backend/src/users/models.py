from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

import constants


class User(AbstractUser):
    """Модель для пользователя."""

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    USER = "user"

    ADMIN = "admin"

    ROLE_USER = [(USER, "Пользователь"), (ADMIN, "Администратор")]

    email = models.EmailField(
        unique=True,
        max_length=constants.MAX_EMAIL_LENGHT,
        verbose_name="Адрес электронной почты",
        help_text="Введите свой адрес электронной почты",
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=constants.MAX_USERNAME_LENGHT,
        unique=True,
        validators=[
            RegexValidator(
                regex=constants.USERNAME_CHECK,
                message="Имя пользователя содержит недопустимый символ",
            )
        ],
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=constants.MAX_FIRST_NAME_LENGHT,
        help_text="Введите свое имя",
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        help_text="Введите свою фамилию",
        max_length=constants.MAX_LAST_NAME_LENGHT,
    )
    role = models.CharField(
        max_length=constants.MAX_ROLE_LENGHT,
        choices=ROLE_USER,
        default=USER,
        verbose_name="Пользовательская роль",
    )
    avatar = models.ImageField(
        upload_to="users/avatar/", blank=False, default=None
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return f"{self.username}"

    @property
    def admin(self):
        """Проверка роли пользователя."""
        return self.role == self.ADMIN


class Follow(models.Model):
    """Модель для подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
        help_text="Текущий пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followed",
        verbose_name="Автор рецепта",
        help_text="Подписаться на автора рецепта(ов)",
    )

    class Meta:
        verbose_name = "Мои подписки"
        verbose_name_plural = "Мои подписки"
        ordering = ("id",)
        constraints = (
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_following"
            ),
        )

    def __str__(self):
        return f"{self.user} подписан на: {self.author}"
