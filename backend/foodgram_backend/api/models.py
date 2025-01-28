from django.db import models
from api.validators import validate_recipe_cooking_time


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Уникальное название',
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Уникальный слаг',
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Список id тегов'
    )
    image = models.ImageField(
        upload_to='api/images/',
        verbose_name='Картинка, закодированная в Base64',
        null=True,
        default=None
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(validate_recipe_cooking_time,)
    )

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
