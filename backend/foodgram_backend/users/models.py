from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    USER = 'user'

    ADMIN = 'admin'

    ROLE_USER = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    ]

    email = models.EmailField(
        unique=True,
        max_length=254,
        db_index=True,
        verbose_name='Адрес электронной почты',
        help_text='Введите свой адрес электронной почты'
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=150,
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r"^[w.@+-]+Z",
            messgae='Недопустимые символы в username.'
        )]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text='Введите свое имя',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Введите свою фамилию',
        max_length=150,
    )
    role = models.CharField(
        max_length=15,
        choices=ROLE_USER,
        default=USER,
        verbose_name='Пользовательская роль'
    )
    # avatar = models.ImageField(
    #     upload_to='users/avatar/',
    #     null=True,
    #     blank=False
    # )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def admin(self):
        return self.role == self.ADMIN

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Текущий пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='Автор рецепта',
        help_text='Подписаться на автора рецепта(ов)'
    )

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на: {self.author}'
