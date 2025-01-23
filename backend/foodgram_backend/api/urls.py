from api.views import IngredientsViewSet, TagsViewSet
from users.views import UsersViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
