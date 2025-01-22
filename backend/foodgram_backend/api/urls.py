from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import IngredientsViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls))
]
