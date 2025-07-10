import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

User = get_user_model()

class Command(BaseCommand):
    """Создает тестовые рецепты от имени существующих пользователей."""

    help = 'Создание нескольких тестовых рецептов'

    def handle(self, *args, **options):
        # --- Получаем исходные данные ---
        # Берем всех пользователей, кроме стаффа/админов
        authors = list(User.objects.filter(is_staff=False))
        tags = list(Tag.objects.all())
        ingredients = list(Ingredient.objects.all())

        # --- Проверяем, есть ли данные для создания рецептов ---
        if not authors:
            self.stdout.write(self.style.ERROR('Нет пользователей для создания рецептов. Сначала создайте их.'))
            return
        if not tags:
            self.stdout.write(self.style.ERROR('Нет тегов для создания рецептов. Сначала создайте их.'))
            return
        if not ingredients:
            self.stdout.write(self.style.ERROR('Нет ингредиентов для создания рецептов. Сначала создайте их.'))
            return

        self.stdout.write('Начинаю создание тестовых рецептов...')

        # --- Создаем 5 тестовых рецептов ---
        for i in range(100):
            recipe_name = f'Тестовый рецепт №{i + 1}'
            
            # Проверяем, не существует ли уже такой рецепт
            if Recipe.objects.filter(name=recipe_name).exists():
                # self.stdout.write(self.style.WARNING(f"Рецепт '{recipe_name}' уже существует. Пропускаю."))
                continue

            # --- Создаем основной объект рецепта ---
            recipe = Recipe.objects.create(
                author=random.choice(authors),
                name=recipe_name,
                text=f'Это подробное описание для тестового рецепта №{i + 1}. Готовить очень просто!',
                cooking_time=random.randint(10, 60)
            )

            # --- Добавляем теги (от 1 до 2 случайных тегов) ---
            recipe.tags.set(random.sample(tags, k=random.randint(1, 2)))

            # --- Добавляем ингредиенты (от 2 до 5 случайных ингредиентов) ---
            selected_ingredients = random.sample(ingredients, k=random.randint(2, 10))
            for ingredient in selected_ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=random.randint(1, 500)
                )
            
            # self.stdout.write(self.style.SUCCESS(f"Рецепт '{recipe_name}' успешно создан."))

        self.stdout.write(self.style.SUCCESS('\nСоздание тестовых рецептов завершено!'))