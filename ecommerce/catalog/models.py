from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from .filter_widgets import FilterWidgetFactory, FilterableMixin
Filters = FilterWidgetFactory.Filters
from .validators import validate_percent, validate_resolution


class ProductManager(models.Manager):
    """ Only published products """
    def get_queryset(self):
        return super().get_queryset().filter(published_at__lte=now())


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    picture = models.ImageField(upload_to='categories')

    details_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    price = models.DecimalField(max_digits=8, decimal_places=2)
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    description = models.TextField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_percent])
    picture = models.ImageField(upload_to='products')
    units_available = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    details_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    details_id = models.PositiveIntegerField()
    details_object = GenericForeignKey("details_content_type", "details_id")

    def __str__(self):
        return self.name

    objects = models.Manager()
    published = ProductManager()

    class Meta:
        indexes = [
            models.Index(fields=["details_content_type", "details_id"]),
        ]


class BaseDetails(FilterableMixin, models.Model):
    def get_short_details(self) -> str:
        """ Returns short string describing most important characteristics (format A/B/C) """
        raise NotImplementedError

    generic_relation_name = None

    class Meta:
        abstract = True


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
        ('has_freezer', Filters.DYNAMIC_CHOICES),  # TODO: add BOOL_CHOICES
        ('EU_energy_label', Filters.DYNAMIC_CHOICES),  # TODO: add STATIC_CHOICES
        ('color', Filters.DYNAMIC_CHOICES)
    ]

    def get_short_details(self) -> str:
        return f"{self.color}/{self.volume_liters}L/{self.EU_energy_label}/{'freezer' if self.has_freezer else 'no freezer'}"

    class Meta:
        verbose_name_plural = 'fridge details'
