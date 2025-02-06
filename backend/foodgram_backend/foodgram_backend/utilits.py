import io
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import base62
from django.urls import reverse


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def create_shopping_cart(ingredients_cart):
    """Функция для формирования списка покупок."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        "attachment; filename='shopping_cart.pdf'"
    )
    pdfmetrics.registerFont(
        TTFont('Arial', 'data/arial.ttf', 'UTF-8')
    )
    buffer = io.BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setFont('Arial', 24)
    pdf_file.drawString(200, 800, 'Список покупок')
    pdf_file.setFont('Arial', 14)
    from_bottom = 750
    for number, ingredient in enumerate(ingredients_cart, start=1):
        pdf_file.drawString(
            50,
            from_bottom,
            f"{number}. {ingredient['ingredient__name']}: "
            f"{ingredient['ingredient_value']} "
            f"{ingredient['ingredient__measurement_unit']}.",
        )
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            pdf_file.showPage()
            pdf_file.setFont('Arial', 14)
    pdf_file.showPage()
    pdf_file.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def generate_short_code(recipe_id):
    """Генерирует короткий код для рецепта"""
    return base62.encode(recipe_id)


def get_short_url(recipe):
    """Возвращает короткий URL для рецепта"""
    return generate_short_code(recipe.id)
