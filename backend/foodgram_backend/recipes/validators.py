from django.core.exceptions import ValidationError

from foodgram_backend import constants


def validate_ingredient_amount(value):
    if not (value <= constants.MIN_INGREDIENT_AMOUNT):
        raise ValidationError('Количество ингридиента должно быть не меньше 1')
    return value
