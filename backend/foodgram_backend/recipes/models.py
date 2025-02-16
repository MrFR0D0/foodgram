from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Уникальное название',
        help_text='Введите название тега',
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Уникальный слаг',
        unique=True,
        help_text='Укажите уникальный слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название',
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единицы измерения',
        help_text='Введите единицу измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка, закодированная в Base64',
        default=None,
        help_text='Добавьте изображение рецепта',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Опишите процесс приготовления',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(
            1,
            'Время приготовления должно быть не меньше 1 минуты'
        )],
        help_text='Укажите время приготовления рецепта в минутах',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        help_text='Автор рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка',
        max_length=20,
        blank=True,
        null=True,
        unique=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='recipe_ingredients',
        help_text='Выберите рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        help_text='Выберите ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            'Минимальное количество ингредиентов 1'
        )],
        help_text='Укажите количество ингредиента')

    class Meta:
        verbose_name = 'Соответствие ингредиента и рецепта'
        verbose_name_plural = 'Таблица соответствия ингредиентов и рецептов'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.recipe} содержит ингредиент/ты {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorite'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('user',)
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
