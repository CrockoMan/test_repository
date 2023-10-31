from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


LENG = 150


class UsernameValidator(UnicodeUsernameValidator):
    """Валидация имени пользователя."""

    regex = r'^[\w.@+-]+\Z'
    flags = 0
    max_length = LENG
    message = (f'Введите правильное имя пользователя. Оно может содержать'
               f' только буквы, цифры и знаки @/./+/-/_.'
               f' Длина не более {LENG} символов')
    error_messages = {
        'invalid': f'Набор символов не более {LENG}. '
                   'Только буквы, цифры и @/./+/-/_',
        'required': 'Поле не может быть пустым',
    }


def check_username_me(value):
    """Проверка имени пользователя (me недопустимое имя)."""
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" не разрешено.'
        )
    return value