from api.filters import IngredientFilter
from api.models import Ingredient, Tag, Recipe, Favorite
from api.serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer
)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_class = IngredientFilter
    pagination_class = None
    search_fields = ['name']
    http_method_names = ('get',)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ('get',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)