from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

import constants
from api.v1.users.serializers import CustomUserSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.utils import Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Промежуточный сериализатор для модели FullIngredientSerializer."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class FullIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientAmount."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при GET запросах."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = FullIngredientSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Recipe при небезопасных запросах."""

    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    ingredients = RecipeIngredientSerializer(
        many=True, allow_empty=False, required=True
    )
    image = Base64ImageField(use_url=True, max_length=None)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def validate_ingredients(self, ingredients):
        """Метод валидации ингридиентов.

        Проверяем, что рецепт содержит уникальные ингредиенты
        и их количество не меньше 1.
        """
        ingredients_data = [ingredient.get("id") for ingredient in ingredients]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise serializers.ValidationError(
                "Ингредиенты рецепта должны быть уникальными"
            )
        for ingredient in ingredients:
            if int(ingredient.get("amount")) < constants.MIN_INGREDIENT_AMOUNT:
                raise serializers.ValidationError(
                    "Количество ингредиента не может быть "
                    f"меньше {constants.MIN_INGREDIENT_AMOUNT}."
                )
            if int(ingredient.get("amount")) > constants.MAX_INGREDIENT_AMOUNT:
                raise serializers.ValidationError(
                    "Количество ингредиента не может быть "
                    f"больше {constants.MAX_INGREDIENT_AMOUNT}."
                )
        return ingredients

    def validate_tags(self, tags):
        """Проверяем, что рецепт содержит уникальные теги."""
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                "Теги рецепта должны быть уникальными."
            )
        return tags

    def validate(self, data):
        """Метод валидации всех данных.

        Проверяем наличие обязательных полей ingredients и tags.
        """
        if "ingredients" not in data:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно."}
            )
        if "tags" not in data:
            raise serializers.ValidationError(
                {"tags": "Это поле обязательно."}
            )
        return data

    @staticmethod
    def add_ingredients(ingredients_data, recipe):
        """Добавляет ингредиенты."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient=ingredient.get("id"),
                    recipe=recipe,
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients_data
            ]
        )

    def update_tags_and_ingredients(self, recipe, tags_data, ingredients_data):
        """Обновляет теги и ингредиенты рецепта.

        Очищает существующие теги и ингредиенты, затем добавляет новые.
        """
        recipe.tags.clear()
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)

    @transaction.atomic
    def create(self, validated_data):
        """Добавляет теги."""
        author = self.context.get("request").user
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.update_tags_and_ingredients(recipe, tags_data, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет теги."""
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        self.update_tags_and_ingredients(instance, tags_data, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = RecipeGETSerializer(recipe)
        return serializer.data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для компактного отображения рецептов."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавляли этот рецепт в избранное",
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавляли этот рецепт в список покупок",
            )
        ]
