import csv
import os
import random
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class Command(BaseCommand):
    """Создает рецепты из CSV-файла, назначая случайных авторов."""

    help = "Загрузка рецептов из файла backend/data/recipes.csv"

    def handle(self, *args, **options):
        """Метод-обработчик."""
        recipes_csv_path = os.path.join(
            settings.BASE_DIR, "..", "data", "recipes.csv"
        )

        # --- Проверка наличия необходимых данных ---
        authors = list(User.objects.filter(is_staff=False))
        if not authors:
            self.stdout.write(
                self.style.ERROR(
                    "Нет пользователей для назначения авторами. \
                        Запустите `import_users`!"
                )
            )
            return

        if not Ingredient.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    "Нет ингредиентов в базе. Запустите `update_ingredients`!"
                )
            )
            return

        # self.stdout.write("Начинаю загрузку рецептов из CSV...")
        created_count = 0
        skipped_count = 0

        try:
            with open(recipes_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    recipe_name = row.get("title", "").strip()
                    if not recipe_name:
                        continue

                    if Recipe.objects.filter(name=recipe_name).exists():
                        skipped_count += 1
                        continue

                    # --- Создание рецепта ---
                    try:
                        # Извлекаем только число из времени приготовления
                        cook_time_str = row.get("cook_time", "0")
                        cook_time_match = re.search(r"\d+", cook_time_str)
                        cooking_time = (
                            int(cook_time_match.group(0))
                            if cook_time_match
                            else 0
                        )

                        # Создаем рецепт без изображения
                        recipe = Recipe.objects.create(
                            author=random.choice(authors),  # noqa: S311
                            name=recipe_name,
                            text=row.get("description", "").strip(),
                            cooking_time=cooking_time,
                        )

                        # --- Прикрепляем изображение ---
                        image_filename = row.get("image", "").strip()
                        if image_filename:
                            image_path = os.path.join(
                                settings.BASE_DIR,
                                "..",
                                "data",
                                "dishes",
                                image_filename,
                            )
                            if os.path.exists(image_path):
                                with open(image_path, "rb") as img_file:
                                    recipe.image.save(
                                        image_filename,
                                        File(img_file),
                                        save=True,
                                    )
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Файл изображения \
                                            '{image_filename}' не найден. \
                                                Рецепт создан без картинки."
                                    )
                                )

                        # --- Добавление тегов ---
                        tag_data = row.get("tag", "").strip().split(",")
                        if len(tag_data) == 2:
                            tag_name, tag_slug = tag_data
                            tag, _ = Tag.objects.get_or_create(
                                name=tag_name.strip(), slug=tag_slug.strip()
                            )
                            recipe.tags.add(tag)

                        # --- Добавление ингредиентов ---
                        ingredients_str = row.get("ingredients", "")
                        ingredient_entries = re.split(
                            r", (?=[А-ЯЁ])", ingredients_str
                        )
                        for entry in ingredient_entries:
                            parts = [p.strip() for p in entry.split("-", 1)]
                            if len(parts) < 2:
                                continue

                            ing_name_raw, amount_raw = parts
                            ing_name = ing_name_raw.lower()

                            amount_match = re.match(r"([\d.,/]+)", amount_raw)
                            amount = (
                                int(
                                    float(
                                        amount_match.group(1).replace(",", ".")
                                    )
                                )
                                if amount_match
                                else 1
                            )

                            # Ищем ингредиент в БД
                            ingredient_obj = Ingredient.objects.filter(
                                name__istartswith=ing_name
                            ).first()
                            if ingredient_obj:
                                RecipeIngredient.objects.create(
                                    recipe=recipe,
                                    ingredient=ingredient_obj,
                                    amount=amount,
                                )
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Ингредиент '{ing_name}' \
                                            не найден. Пропускаю."
                                    )
                                )

                        created_count += 1
                        # self.stdout.write(self.style.SUCCESS(f"Рецепт \
                        #     '{recipe_name}' успешно создан."))

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Ошибка при создании рецепта \
                                    '{recipe_name}': {e}!"
                            )
                        )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Файл не найден: {recipes_csv_path}!")
            )
            return

        # self.stdout.write("\n--- Статистика ---")
        # self.stdout.write(self.style.SUCCESS(f"Создано новых рецептов: \
        #     {created_count}"))
        # self.stdout.write(self.style.WARNING(f"Пропущено (уже существуют): \
        #     {skipped_count}"))
        self.stdout.write(self.style.SUCCESS("Загрузка рецептов завершена."))
