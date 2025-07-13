from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс настройки раздела тегов."""

    list_display = ("pk", "name", "slug")
    list_display_links = ("pk", "name")
    empty_value_display = "значение отсутствует"
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс настройки раздела ингредиентов."""

    list_display = ("pk", "name", "measurement_unit")
    list_display_links = ("pk", "name")
    empty_value_display = "значение отсутствует"
    search_fields = ("name",)


class IngredientAmountInline(admin.TabularInline):
    """Класс, позволяющий добавлять ингредиенты в рецепты."""

    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс настройки раздела рецептов."""

    list_display = (
        "pk",
        "name",
        "author",
        "text",
        "get_tags",
        "get_ingredients",
        "cooking_time",
        "image",
        "pub_date",
        "count_favorite",
    )
    inlines = [IngredientAmountInline]
    list_display_links = ("pk", "name")
    empty_value_display = "значение отсутствует"
    list_filter = ("tags", "author")
    search_fields = ("name",)

    def get_queryset(self, request):
        """Получение рецепта."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("author").prefetch_related(
            "tags", "recipe_ingredients__ingredient"
        )
        return queryset

    def get_ingredients(self, object):
        """Получает ингредиент или список ингредиентов рецепта."""
        return "\n".join(
            (ingredient.name for ingredient in object.ingredients.all())
        )

    get_ingredients.short_description = "ингредиенты"

    def get_tags(self, object):
        """Получает тег или список тегов рецепта."""
        return "\n".join((tag.name for tag in object.tags.all()))

    get_tags.short_description = "теги"

    def count_favorite(self, object):
        """Вычисляет количество добавлений рецепта в избранное."""
        return object.favorite.count()

    count_favorite.short_description = "Количество добавлений в избранное"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Класс настройки соответствия игредиентов и рецептов."""

    list_display = ("pk", "recipe", "ingredient", "amount")
    empty_value_display = "значение отсутствует"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс настройки раздела избранного."""

    list_display = ("pk", "user", "recipe")

    def get_queryset(self, request):
        """Получает избранное."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            "user", "recipe__author"
        ).prefetch_related(
            "recipe__tags", "recipe__recipe_ingredients__ingredient"
        )
        return queryset

    empty_value_display = "значение отсутствует"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс настройки раздела рецептов, которые добавлены в список покупок."""

    list_display = ("pk", "user", "recipe")
    list_display_links = ("pk", "user")

    def get_queryset(self, request):
        """Получает объект списка покупок."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            "user", "recipe__author"
        ).prefetch_related(
            "recipe__tags", "recipe__recipe_ingredients__ingredient"
        )
        return queryset

    empty_value_display = "значение отсутствует"
