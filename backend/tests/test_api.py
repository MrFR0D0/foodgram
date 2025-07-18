import pytest
from django.contrib.auth import get_user_model
from jsonschema import validate
from rest_framework.test import APIClient

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Follow

User = get_user_model()

# Schemas

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "is_subscribed": {"type": "boolean"}
    },
    "required": ["email", "id", "username", "first_name", "last_name", "is_subscribed"]
}

USER_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
    },
    "required": ["email", "id", "username", "first_name", "last_name"]
}

RECIPE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "tags": {"type": "array", "items": {"type": "object"}},
        "author": USER_SCHEMA,
        "ingredients": {"type": "array", "items": {"type": "object"}},
        "is_favorited": {"type": "boolean"},
        "is_in_shopping_cart": {"type": "boolean"},
        "name": {"type": "string"},
        "image": {"type": ["string", "null"], "format": "uri"},
        "text": {"type": "string"},
        "cooking_time": {"type": "integer"}
    },
    "required": ["id", "tags", "author", "ingredients", "is_favorited", "is_in_shopping_cart", "name", "image", "text", "cooking_time"]
}

PAGINATED_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"], "format": "uri"},
        "previous": {"type": ["string", "null"], "format": "uri"},
        "results": {"type": "array", "items": USER_SCHEMA}
    },
    "required": ["count", "next", "previous", "results"]
}

PAGINATED_RECIPE_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"], "format": "uri"},
        "previous": {"type": ["string", "null"], "format": "uri"},
        "results": {"type": "array", "items": RECIPE_SCHEMA}
    },
    "required": ["count", "next", "previous", "results"]
}

# Fixtures

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def user_factory(**kwargs):
        return User.objects.create_user(**kwargs)
    return user_factory

@pytest.fixture
def create_tag(db):
    def tag_factory(**kwargs):
        return Tag.objects.create(**kwargs)
    return tag_factory

@pytest.fixture
def create_ingredient(db):
    def ingredient_factory(**kwargs):
        return Ingredient.objects.create(**kwargs)
    return ingredient_factory

@pytest.fixture
def create_recipe(db, create_user, create_tag, create_ingredient):
    def recipe_factory(**kwargs):
        user = kwargs.pop('author', None)
        if user is None:
            user = create_user(email='test@test.com', username='test', password='test')
        tag = create_tag(name='Test Tag', slug='test-tag')
        ingredient = create_ingredient(name='Test Ingredient', measurement_unit='g')
        recipe = Recipe.objects.create(author=user, **kwargs)
        recipe.tags.add(tag)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=100)
        return recipe
    return recipe_factory

# User and Auth Tests

@pytest.mark.django_db
class TestUsers:
    def test_create_user(self, client):
        response = client.post('/api/users/', {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword'
        })
        assert response.status_code == 201
        validate(instance=response.json(), schema=USER_CREATE_SCHEMA)

    def test_get_token(self, client, create_user):
        create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        response = client.post('/api/auth/token/login/', {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        })
        assert response.status_code == 200
        validate(instance=response.json(), schema={"type": "object", "properties": {"auth_token": {"type": "string"}}, "required": ["auth_token"]})

    @pytest.mark.parametrize("missing_field", ["email", "username", "first_name", "last_name", "password"])
    def test_create_user_missing_fields(self, client, missing_field):
        data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword'
        }
        del data[missing_field]
        response = client.post('/api/users/', data)
        assert response.status_code == 400

    def test_create_user_duplicate_email(self, client, create_user):
        create_user(
            email='testuser@example.com',
            username='testuser1',
            password='testpassword'
        )
        response = client.post('/api/users/', {
            'email': 'testuser@example.com',
            'username': 'testuser2',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword'
        })
        assert response.status_code == 400

    def test_create_user_duplicate_username(self, client, create_user):
        create_user(
            email='testuser1@example.com',
            username='testuser',
            password='testpassword'
        )
        response = client.post('/api/users/', {
            'email': 'testuser2@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword'
        })
        assert response.status_code == 400

    def test_create_user_invalid_username(self, client):
        response = client.post('/api/users/', {
            'email': 'testuser@example.com',
            'username': 'invalid-username!',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword'
        })
        assert response.status_code == 400

    @pytest.mark.parametrize("field, value", [
        ("email", "a" * 255 + "@example.com"),
        ("username", "a" * 151),
        ("first_name", "a" * 151),
        ("last_name", "a" * 151),
    ])
    def test_create_user_too_long_fields(self, client, field, value):
        data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword'
        }
        data[field] = value
        response = client.post('/api/users/', data)
        assert response.status_code == 400

    def test_get_user_list_unauthenticated(self, client):
        response = client.get('/api/users/')
        assert response.status_code == 200

    def test_get_user_list_authenticated(self, client, create_user):
        user = create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        client.force_authenticate(user=user)
        response = client.get('/api/users/')
        assert response.status_code == 200
        validate(instance=response.json(), schema=PAGINATED_USER_SCHEMA)

    def test_get_user_profile(self, client, create_user):
        user = create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        response = client.get(f'/api/users/{user.id}/')
        assert response.status_code == 200
        validate(instance=response.json(), schema=USER_SCHEMA)

    def test_get_me(self, client, create_user):
        user = create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        client.force_authenticate(user=user)
        response = client.get('/api/users/me/')
        assert response.status_code == 200
        validate(instance=response.json(), schema=USER_SCHEMA)

# Recipe Tests

@pytest.mark.django_db
class TestRecipes:
    def test_create_recipe(self, client, create_user, create_tag, create_ingredient):
        user = create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        tag = create_tag(name='Test Tag', slug='test-tag')
        ingredient = create_ingredient(name='Test Ingredient', measurement_unit='g')
        client.force_authenticate(user=user)
        response = client.post('/api/recipes/', {
            'ingredients': [{'id': ingredient.id, 'amount': 100}],
            'tags': [tag.id],
            'name': 'Test Recipe',
            'text': 'Test recipe text',
            'cooking_time': 10,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
        }, format='json')
        assert response.status_code == 201
        validate(instance=response.json(), schema=RECIPE_SCHEMA)

    def test_get_recipe_list(self, client, create_recipe):
        create_recipe(name='Test Recipe', text='Test recipe text', cooking_time=10)
        response = client.get('/api/recipes/')
        assert response.status_code == 200
        validate(instance=response.json(), schema=PAGINATED_RECIPE_SCHEMA)

    def test_get_recipe_detail(self, client, create_recipe):
        recipe = create_recipe(name='Test Recipe', text='Test recipe text', cooking_time=10)
        response = client.get(f'/api/recipes/{recipe.id}/')
        assert response.status_code == 200
        validate(instance=response.json(), schema=RECIPE_SCHEMA)

    def test_add_recipe_to_favorites(self, client, create_user, create_recipe):
        user = create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        recipe = create_recipe(author=user, name='Test Recipe', text='Test recipe text', cooking_time=10)
        client.force_authenticate(user=user)
        response = client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == 201
        assert Favorite.objects.filter(user=user, recipe=recipe).exists()

    def test_add_recipe_to_shopping_cart(self, client, create_user, create_recipe):
        user = create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        recipe = create_recipe(author=user, name='Test Recipe', text='Test recipe text', cooking_time=10)
        client.force_authenticate(user=user)
        response = client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == 201
        assert ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

# Tag and Ingredient Tests

@pytest.mark.django_db
class TestTagsAndIngredients:
    def test_get_tag_list(self, client):
        response = client.get('/api/tags/')
        assert response.status_code == 200

    def test_get_tag_detail(self, client, create_tag):
        tag = create_tag(name='Test Tag', slug='test-tag')
        response = client.get(f'/api/tags/{tag.id}/')
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Test Tag'

    def test_get_ingredient_list(self, client):
        response = client.get('/api/ingredients/')
        assert response.status_code == 200

    def test_get_ingredient_detail(self, client, create_ingredient):
        ingredient = create_ingredient(name='Test Ingredient', measurement_unit='g')
        response = client.get(f'/api/ingredients/{ingredient.id}/')
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Test Ingredient'

# Subscription Tests

@pytest.mark.django_db
class TestSubscriptions:
    def test_subscribe(self, client, create_user):
        user1 = create_user(email='user1@example.com', username='user1', password='testpassword')
        user2 = create_user(email='user2@example.com', username='user2', password='testpassword')
        client.force_authenticate(user=user1)
        response = client.post(f'/api/users/{user2.id}/subscribe/')
        assert response.status_code == 201
        assert Follow.objects.filter(user=user1, author=user2).exists()

    def test_unsubscribe(self, client, create_user):
        user1 = create_user(email='user1@example.com', username='user1', password='testpassword')
        user2 = create_user(email='user2@example.com', username='user2', password='testpassword')
        Follow.objects.create(user=user1, author=user2)
        client.force_authenticate(user=user1)
        response = client.delete(f'/api/users/{user2.id}/subscribe/')
        assert response.status_code == 204
        assert not Follow.objects.filter(user=user1, author=user2).exists()

    def test_get_subscriptions(self, client, create_user):
        user = create_user(email='user@example.com', username='user', password='testpassword')
        client.force_authenticate(user=user)
        response = client.get('/api/users/subscriptions/')
        assert response.status_code == 200
