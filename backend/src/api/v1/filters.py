import django_filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="istartswith"
    )

    class Meta:
        model = Ingredient
        fields = ["name"]


class MultipleValueFilter(
    django_filters.BaseInFilter, django_filters.CharFilter
):
    """Фильтр для множественных значений."""

    pass


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""

    tags = MultipleValueFilter(field_name="tags__slug", lookup_expr="in")
    is_favorited = django_filters.NumberFilter(method="get_is_favorited")
    is_in_shopping_cart = django_filters.NumberFilter(
        method="get_is_in_shopping_cart"
    )
    author = django_filters.AllValuesMultipleFilter(field_name="author__id")

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, queryset, name, value):
        """Фильтрация избранных рецептов."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов из списка покупок."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
