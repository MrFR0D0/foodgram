from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.recipes.views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
)
from api.v1.users.views import CustomUserViewSet

app_name = "api"

router = DefaultRouter()
router.register(r"ingredients", IngredientsViewSet, basename="ingredients")
router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"recipes", RecipesViewSet, basename="recipes")
router.register(r"users", CustomUserViewSet, basename="users")
urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
