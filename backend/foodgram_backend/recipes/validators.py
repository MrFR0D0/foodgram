from django.core.exceptions import ValidationError


def validate_ingredient_amount(value):
    if not (value <= 1):
        raise ValidationError('Количество ингридиента должно быть не меньше 1')
    return value
