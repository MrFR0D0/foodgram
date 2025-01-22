from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from rest_framework import viewsets
from api.serializers import IngredientSerializer
from api.models import Ingredient
from api.filters import IngredientFilter


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_class = IngredientFilter
    search_fields = ['name']
    http_method_names = ('get',)
