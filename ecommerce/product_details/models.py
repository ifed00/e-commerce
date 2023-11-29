from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from catalog.models import BaseDetails, Product
from catalog.validators import positive_decimal_validator
from orders.validators import non_zero_validator
from catalog.filters import Filters


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

    generic_relation_name = 'garlands'

    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('working_modes', Filters.BOUND),
        ('length_meters', Filters.BOUND),
        ('bulb_form', Filters.DYNAMIC_CHOICES),
        ('color', Filters.DYNAMIC_CHOICES)
    ]


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

    generic_relation_name = 'illuminations'

    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('is_candle', Filters.BOOL_CHOICES),
        ('length_cm', Filters.BOUND),
        ('width_cm', Filters.BOUND),
        ('height_cm', Filters.BOUND),
        ('form', Filters.DYNAMIC_CHOICES),
        ('color', Filters.DYNAMIC_CHOICES)
    ]


class WreathDetails(BaseDetails):
    material = models.CharField(max_length=256)
    length_cm = DimensionField()
    width_cm = DimensionField()
    color = ColorField()
    has_illumination = models.BooleanField()

    def get_short_details(self) -> str:
        return f'mostly {self.color}/{self.material}/{self.length_cm}x{self.width_cm} cm' \
               f'{"/illuminated" if self.has_illumination else ""}'

    generic_relation_name = 'wreaths'

    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('material', Filters.DYNAMIC_CHOICES),
        ('length_cm', Filters.BOUND),
        ('width_cm', Filters.BOUND),
        ('has_illumination', Filters.BOOL_CHOICES),
        ('color', Filters.DYNAMIC_CHOICES)
    ]


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
    quantity = models.PositiveIntegerField(default=1, validators=[non_zero_validator])
    color = ColorField()

    def get_short_details(self) -> str:
        return f'{self.get_type_display()}/{self.quantity} in set/{self.length_cm}x{self.width_cm}x{self.height_cm} cm/' \
               f'{self.color}/{self.material}'

    generic_relation_name = 'decorations'

    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('type', Filters.STATIC_CHOICES),
        ('length_cm', Filters.BOUND),
        ('width_cm', Filters.BOUND),
        ('height_cm', Filters.BOUND),
        ('quantity', Filters.BOUND),
        ('has_illumination', Filters.BOOL_CHOICES),
        ('material', Filters.DYNAMIC_CHOICES),
        ('color', Filters.DYNAMIC_CHOICES)
    ]


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

    generic_relation_name = 'gift_wrap'

    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('length_cm', Filters.BOUND),
        ('width_cm', Filters.BOUND),
        ('density', Filters.BOUND),
        ('has_accent', Filters.BOOL_CHOICES),
        ('has_print', Filters.BOOL_CHOICES),
        ('is_monochrome', Filters.BOOL_CHOICES),
        ('color', Filters.DYNAMIC_CHOICES)
    ]


class FireworksDetails(BaseDetails):
    shots = models.PositiveIntegerField()
    duration_seconds = models.PositiveIntegerField(validators=[non_zero_validator])
    main_effect = models.CharField(max_length=256)
    number_of_effects = models.PositiveIntegerField(validators=[non_zero_validator])
    color = ColorField()

    def get_short_details(self) -> str:
        return f'{self.main_effect}/mostly {self.color}/{self.number_of_effects} effects/{self.shots} shots/{self.duration_seconds} s'

    generic_relation_name = 'fireworks'

    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('shots', Filters.BOUND),
        ('duration_seconds', Filters.BOUND),
        ('main_effect', Filters.DYNAMIC_CHOICES),
        ('number_of_effects', Filters.BOUND),
        ('color', Filters.DYNAMIC_CHOICES)
    ]
