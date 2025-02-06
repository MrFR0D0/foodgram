from api.views import IngredientsViewSet, TagsViewSet, RecipesViewSet
from django.urls import include, path, re_path
from users.views import CustomUserViewSet

from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'users', CustomUserViewSet, basename='users')
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
