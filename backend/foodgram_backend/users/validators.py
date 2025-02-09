import re

from rest_framework.exceptions import ValidationError

from foodgram_backend import constants


def username_validator(value):
    regex = constants.USERNAME_CHECK
    if re.search(regex, value) is None:
        invalid_characters = set(re.findall(r"^[w.@+-]+Z", value))
        raise ValidationError(
            (
                f"Не допустимые символы {invalid_characters} в username. "
                f"username может содержать только буквы, цифры и "
                f"знаки @/./+/-/_."
            ),
        )
    return value
