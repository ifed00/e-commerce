import re
from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_percent(input_data: Decimal) -> None:
    if input_data < 0 or input_data > 100:
        raise ValidationError(f'{input_data = }, but should be positive and less or equal to 100',
                              code='out_of_range')


def validate_resolution(input_data: str) -> None:
    split_data = input_data.split('x')
    if len(split_data) != 2:
        raise ValidationError(f"{input_data = } is not resolution", code='bad_resolution')

    if not re.fullmatch('\d+', split_data[0]) or not re.fullmatch('\d+', split_data[1]):
        raise ValidationError(f"{input_data} is not resolution", code='bad_height_width_value')

    h, w = int(split_data[0]), int(split_data[1])

    if h == 0 or w == 0 or \
            str(h) != split_data[0] or str(w) != split_data[1]:
        raise ValidationError(f"{input_data} contains ill-formed integers", code='bad_int_format')
