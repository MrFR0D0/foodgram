from django.core.exceptions import ValidationError

import constants


def validate_ingredient_amount(value):
    """Проверка количества ингридиентов."""
    if not (value <= constants.MIN_INGREDIENT_AMOUNT):
        raise ValidationError("Количество ингридиента должно быть не меньше 1")
    return value
