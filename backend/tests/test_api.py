
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

User = get_user_model()

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

@pytest.mark.django_db
def test_create_user(client):
    response = client.post('/api/users/', {
        'email': 'testuser@example.com',
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    data = response.json()
    assert data['email'] == 'testuser@example.com'
    assert data['username'] == 'testuser'

@pytest.mark.django_db
def test_get_token(client, create_user):
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
    data = response.json()
    assert 'auth_token' in data

@pytest.mark.django_db
@pytest.mark.parametrize("missing_field", ["email", "username", "first_name", "last_name", "password"])
def test_create_user_missing_fields(client, missing_field):
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

@pytest.mark.django_db
def test_get_user_list_unauthenticated(client):
    response = client.get('/api/users/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_user_list_authenticated(client, create_user):
    user = create_user(
        email='testuser@example.com',
        username='testuser',
        password='testpassword'
    )
    client.force_authenticate(user=user)
    response = client.get('/api/users/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_user_profile(client, create_user):
    user = create_user(
        email='testuser@example.com',
        username='testuser',
        password='testpassword'
    )
    response = client.get(f'/api/users/{user.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'testuser'

@pytest.mark.django_db
def test_get_me(client, create_user):
    user = create_user(
        email='testuser@example.com',
        username='testuser',
        password='testpassword'
    )
    client.force_authenticate(user=user)
    response = client.get('/api/users/me/')
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'testuser'

@pytest.mark.django_db
def test_create_recipe(client, create_user, create_tag, create_ingredient):
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
    data = response.json()
    assert data['name'] == 'Test Recipe'

@pytest.mark.django_db
def test_get_recipe_list(client):
    response = client.get('/api/recipes/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_recipe_detail(client, create_recipe):
    recipe = create_recipe(name='Test Recipe', text='Test recipe text', cooking_time=10)
    response = client.get(f'/api/recipes/{recipe.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Test Recipe'

@pytest.mark.django_db
def test_add_recipe_to_favorites(client, create_user, create_recipe):
    user = create_user(
        email='testuser@example.com',
        username='testuser',
        password='testpassword'
    )
    recipe = create_recipe(author=user, name='Test Recipe', text='Test recipe text', cooking_time=10)
    client.force_authenticate(user=user)
    response = client.post(f'/api/recipes/{recipe.id}/favorite/')
    assert response.status_code == 201

@pytest.mark.django_db
def test_add_recipe_to_shopping_cart(client, create_user, create_recipe):
    user = create_user(
        email='testuser@example.com',
        username='testuser',
        password='testpassword'
    )
    recipe = create_recipe(author=user, name='Test Recipe', text='Test recipe text', cooking_time=10)
    client.force_authenticate(user=user)
    response = client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
    assert response.status_code == 201

@pytest.mark.django_db
def test_get_tag_list(client):
    response = client.get('/api/tags/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_tag_detail(client, create_tag):
    tag = create_tag(name='Test Tag', slug='test-tag')
    response = client.get(f'/api/tags/{tag.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Test Tag'

@pytest.mark.django_db
def test_get_ingredient_list(client):
    response = client.get('/api/ingredients/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_ingredient_detail(client, create_ingredient):
    ingredient = create_ingredient(name='Test Ingredient', measurement_unit='g')
    response = client.get(f'/api/ingredients/{ingredient.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Test Ingredient'
