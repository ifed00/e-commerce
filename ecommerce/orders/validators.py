from decimal import Decimal

from django.core.exceptions import ValidationError


def non_zero_validator(input_data: Decimal) -> None:
    if input_data == 0:
        raise ValidationError(f'input_data is zero which is forbidden')
