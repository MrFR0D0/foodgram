from api.filters import IngredientFilter
from api.models import Ingredient, Tag
from api.serializers import IngredientSerializer, TagSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_class = IngredientFilter
    search_fields = ['name']
    http_method_names = ('get',)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ('get',)
