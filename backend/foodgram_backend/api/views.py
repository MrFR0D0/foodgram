from api.filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart, RecipeIngredient)
from api.serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    FavoriteSerializer, RecipeShortSerializer, ShoppingCartSerializer,
    RecipeGETSerializer)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from api.permissions import AuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Sum
from foodgram_backend.utilits import create_shopping_cart


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    http_method_names = ('get',)  # Возможно это лишнее.


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend,]
    filterset_class = IngredientFilter
    pagination_class = None
    search_fields = ['name']
    http_method_names = ('get',)  # Возможно это лишнее.


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        url_name='favorite', permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = RecipeShortSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        favorite_recipe = get_object_or_404(
            Favorite, user=request.user, recipe=recipe
        )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        url_name='shopping_cart', permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        """Позволяет текущему пользователю добавлять рецепты
        в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = RecipeShortSerializer(recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED
            )
        shopping_cart_recipe = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        shopping_cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        url_name='download_shopping_cart', url_path='download_shopping_cart',
        detail=False, methods=['get'], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_cart = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        return create_shopping_cart(ingredients_cart)

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer
