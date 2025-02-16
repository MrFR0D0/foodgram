from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import AuthorOrReadOnly
from api.serializers.recipes import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeGETSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.utils import create_shopping_cart


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    search_fields = ['name']
    http_method_names = ('get',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def base_post_or_delete(self, request, pk, model, serializer_class):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = serializer_class(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            object_serializer = RecipeShortSerializer(recipe)
            return Response(
                object_serializer.data, status=status.HTTP_201_CREATED
            )
        deleted_count, _ = model.objects.filter(
            user=request.user, recipe__id=pk
        ).delete()
        if deleted_count == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        url_name='favorite', permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        return self.base_post_or_delete(
            request=request, pk=pk, model=Favorite,
            serializer_class=FavoriteSerializer,
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        url_name='shopping_cart', permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        """Метод списка покупок.

        Позволяет текущему пользователю добавлять/удалять рецепты
        в список покупок.
        """
        return self.base_post_or_delete(
            request=request, pk=pk, model=ShoppingCart,
            serializer_class=ShoppingCartSerializer,
        )

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
        buffer = create_shopping_cart(ingredients_cart)
        return HttpResponse(
            buffer,
            content_type='text/plain'
        )

    def get_serializer_class(self):
        """Метод определения сериализатора.

        Определяет какой сериализатор будет использоваться
        для разных типов запроса.
        """
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer

    @action(
        detail=True, methods=['get'], url_path='get-link',
        url_name='get-link', permission_classes=(AllowAny,),
    )
    def get_short_link(self, request, pk):
        """Возвращает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        rev_link = reverse('short_url', args=[recipe.pk])
        return Response(
            {'short-link': request.build_absolute_uri(rev_link)},
            status=status.HTTP_200_OK
        )


def short_url(request, short_link):
    """Редирект с короткой ссылки."""
    link = request.build_absolute_uri()
    recipe = get_object_or_404(Recipe, short_link=link)
    return redirect(
        'api:recipe-detail',
        pk=recipe.id
    )
