from django.db import models

from catalog.models import BaseDetails
from catalog.validators import positive_decimal_validator
from orders.validators import non_zero_validator


class ColorField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 64
        super().__init__(*args, **kwargs)


class DimensionField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        validators = kwargs.get('validators', [])
        validators.append(positive_decimal_validator)
        kwargs['validators'] = validators
        kwargs['max_digits'] = 5
        kwargs['decimal_places'] = 2
        super().__init__(*args, **kwargs)


class GarlandDetails(BaseDetails):
    working_modes = models.PositiveIntegerField(default=1, validators=[non_zero_validator])
    length_meters = DimensionField()
    bulb_form = models.CharField(max_length=64)
    color = ColorField()

    def get_short_details(self) -> str:
        return f'{self.working_modes} modes/{self.length_meters} m/' \
               f'{self.bulb_form}/{self.color}'


class IlluminationDetails(BaseDetails):
    color = ColorField()
    form = models.CharField(max_length=64)
    length_cm = DimensionField()
    width_cm = DimensionField()
    height_cm = DimensionField()
    is_candle = models.BooleanField()

    def get_short_details(self) -> str:
        return f'{self.color}/{self.form}/{self.length_cm}x{self.width_cm}x{self.height_cm} cm/' \
               f'{"candle" if self.is_candle else "electric lamp"}'


class WreathDetails(BaseDetails):
    material = models.CharField(max_length=256)
    length_cm = DimensionField()
    width_cm = DimensionField()
    color = ColorField()
    has_illumination = models.BooleanField()

    def get_short_details(self) -> str:
        return f'mostly {self.color}/{self.material}/{self.length_cm}x{self.width_cm} cm' \
               f'{"/illuminated" if self.has_illumination else ""}'


class DecorationDetails(BaseDetails):
    DECORATION_CHOICES = [
        ('ORN', 'Ornaments'),
        ('CHR', 'Characters'),
        ('ANI', 'Animals'),
        ('SNW', 'Snowflakes'),
        ('OTR', 'Others')
    ]
    type = models.CharField(max_length=3, choices=DECORATION_CHOICES)
    length_cm = DimensionField()
    width_cm = DimensionField()
    height_cm = DimensionField()
    material = models.CharField(max_length=256)
    color = ColorField()

    def get_short_details(self) -> str:
        return f'{self.type}/{self.length_cm}x{self.width_cm}x{self.height_cm} cm/' \
               f'{self.color}/{self.material}'


class GiftWrapDetails(BaseDetails):
    color = ColorField()
    density = models.CharField(max_length=64)
    length_cm = DimensionField()
    width_cm = DimensionField()
    has_accent = models.BooleanField()
    has_print = models.BooleanField()
    is_monochrome = models.BooleanField()

    def get_short_details(self) -> str:
        return f'{self.color}/{self.density}/{self.length_cm}x{self.width_cm} cm/' \
               f'{"has print/" if self.has_print else ""}{"monochrome/" if self.is_monochrome else ""}' \
               f'{"has accent picture" if self.has_accent else ""}'


class FireworksDetails(BaseDetails):
    shots = models.PositiveIntegerField()
    duration_seconds = models.PositiveIntegerField(validators=[non_zero_validator])
    main_effect = models.CharField(max_length=256)
    number_of_effects = models.PositiveIntegerField(validators=[non_zero_validator])
    color = ColorField()

    def get_short_details(self) -> str:
        return f'{self.main_effect}/mostly {self.color}/{self.number_of_effects} effects/{self.shots} shots/{self.duration_seconds} s'
