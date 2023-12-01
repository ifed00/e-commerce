from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from catalog.filters import Filters
from catalog.models import Product, BaseDetails
from catalog.validators import validate_resolution


# Create your models here.


class PhoneDetails(BaseDetails):
    memory_KB = models.PositiveIntegerField()
    display_resolution = models.CharField(max_length=16, validators=[validate_resolution])
    camera_resolution = models.CharField(max_length=16, validators=[validate_resolution])
    color = models.CharField(max_length=32)

    generic_relation_name = 'phones'

    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('memory_KB', Filters.BOUND),
        ('display_resolution', Filters.DYNAMIC_CHOICES),
        ('camera_resolution', Filters.DYNAMIC_CHOICES),
        ('color', Filters.DYNAMIC_CHOICES)
    ]

    def get_short_details(self) -> str:
        return f"{self.color}/{self.display_resolution}/{int(self.memory_KB) / 1024 / 1024}GB"

    class Meta:
        verbose_name_plural = 'phone details'


class FridgeDetails(BaseDetails):
    EU_ENERGY_LABEL_CHOICES = [
        ('A+++', 'A+++'),
        ('A++', 'A++'),
        ('A+', 'A+'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G')
    ]

    volume_liters = models.PositiveIntegerField()
    has_freezer = models.BooleanField()
    color = models.CharField(max_length=32, default='White')
    EU_energy_label = models.CharField(max_length=8, choices=EU_ENERGY_LABEL_CHOICES)

    generic_relation_name = 'fridges'
    product = GenericRelation(Product, related_query_name=generic_relation_name,
                              content_type_field='details_content_type', object_id_field='details_id')

    FILTERS = [
        ('volume_liters', Filters.BOUND),
        ('has_freezer', Filters.BOOL_CHOICES),
        ('EU_energy_label', Filters.STATIC_CHOICES),
        ('color', Filters.DYNAMIC_CHOICES)
    ]

    def get_short_details(self) -> str:
        return f"{self.color}/{self.volume_liters}L/{self.EU_energy_label}/{'freezer' if self.has_freezer else 'no freezer'}"

    class Meta:
        verbose_name_plural = 'fridge details'
