import base64
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class Command(BaseCommand):
    """Команда управления Django для экспорта данных в файл JSON."""

    help = "Экспорт данных в JSON"

    def handle(self, *args, **options):
        """Обработка выполнения команды."""
        self.stdout.write("Экспорт данных...")

        users = User.objects.all()
        recipes = Recipe.objects.all()
        tags = Tag.objects.all()
        ingredients = Ingredient.objects.all()

        data = {"users": [], "recipes": [], "tags": [], "ingredients": []}

        for user in users:
            avatar_data = None
            if user.avatar:
                try:
                    with open(user.avatar.path, "rb") as image_file:
                        avatar_data = (
                            f"data:image/png;base64,"
                            f"{base64.b64encode(image_file.read()).decode('utf-8')}"
                        )
                except FileNotFoundError:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Avatar not found for user {user.id}"
                        )
                    )

            data["users"].append(
                {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "avatar": avatar_data,
                }
            )

        for tag in tags:
            data["tags"].append(
                {"id": tag.id, "name": tag.name, "slug": tag.slug}
            )

        for ingredient in ingredients:
            data["ingredients"].append(
                {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "measurement_unit": ingredient.measurement_unit,
                }
            )

        for recipe in recipes:
            image_data = None
            if recipe.image:
                try:
                    with open(recipe.image.path, "rb") as image_file:
                        image_data = (
                            f"data:image/png;base64,"
                            f"{base64.b64encode(image_file.read()).decode('utf-8')}"
                        )
                except FileNotFoundError:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Image not found for recipe {recipe.id}"
                        )
                    )

            ingredients_data = [
                {
                    "id": item.ingredient.id,
                    "name": item.ingredient.name,
                    "measurement_unit": item.ingredient.measurement_unit,
                    "amount": item.amount,
                }
                for item in recipe.recipe_ingredients.all()
            ]
            data["recipes"].append(
                {
                    "id": recipe.id,
                    "author": recipe.author.id,
                    "name": recipe.name,
                    "image": image_data,
                    "text": recipe.text,
                    "cooking_time": recipe.cooking_time,
                    "tags": [tag.id for tag in recipe.tags.all()],
                    "ingredients": ingredients_data,
                }
            )

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        self.stdout.write(
            self.style.SUCCESS("Данные успешно экспортированы в data.json")
        )
