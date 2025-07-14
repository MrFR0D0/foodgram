import base64
import io

import base62
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для изображений, закодированных в строку Base64."""

    def to_internal_value(self, data):
        """Преобразует строку Base64 data URI в объект файла."""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


def create_shopping_cart(ingredients_cart):
    """Функция для формирования списка покупок."""
    shopping_list = "\n".join(
        f"{ingredient['ingredient__name']} - {ingredient['ingredient_value']} "
        f"({ingredient['ingredient__measurement_unit']})"
        for ingredient in ingredients_cart
    )
    buffer = io.BytesIO()
    buffer.write(shopping_list.encode("utf-8"))
    buffer.seek(0)
    return buffer


def generate_short_code(recipe_id):
    """Генерирует короткий код для рецепта."""
    return base62.encode(recipe_id)


def get_short_url(recipe):
    """Возвращает короткий URL для рецепта."""
    return generate_short_code(recipe.id)
