from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.utils import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.utils import get_short_url
from api.serializers.users import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=32,
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Промежуточный сериализатор для модели FullIngredientSerializer."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class FullIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientAmount."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при GET запросах."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    @staticmethod
    def get_ingredients(object):
        """Получает ингредиенты из модели RecipeIngredient."""
        ingredients = RecipeIngredient.objects.filter(recipe=object)
        return FullIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, object):
        """Проверяет, добавил ли текущий пользователь рецепт в избранное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        """Проверяет, добавил ли текущий пользователь рецепт в корзину."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=object).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при небезопасных запросах."""

    ingredients = RecipeIngredientSerializer(
        many=True,
        allow_empty=False,
    )
    image = Base64ImageField(
        use_url=True,
        max_length=None
    )
    author = CustomUserSerializer(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def create(self, validated_data):
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.short_link = get_short_url(recipe)
        recipe.save()
        return recipe

    def validate_ingredients(self, ingredients):
        """
        Метод валидации ингридиентов.

        Проверяем, что рецепт содержит уникальные ингредиенты
        и их количество не меньше 1.
        """
        ingredients_data = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                'Ингредиенты рецепта должны быть уникальными'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
            if int(ingredient.get('amount')) > 100:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть больше 100'
                )
        return ingredients

    def validate_tags(self, tags):
        """Проверяем, что рецепт содержит уникальные теги."""
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги рецепта должны быть уникальными'
            )
        return tags

    @staticmethod
    def add_ingredients(ingredients_data, recipe):
        """Добавляет ингредиенты."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = validated_data.get('tags')
        instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.add_ingredients(ingredients_data, instance)
        validated_data.pop('ingredients', None)
        validated_data.pop('tags', None)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = RecipeGETSerializer(recipe)
        return serializer.data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для компактного отображения рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли этот рецепт в избранное'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли это рецепт в список покупок'
            )
        ]
