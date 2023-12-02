from decimal import Decimal

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now

from .filters import FilterableMixin, Filters
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

    def get_absolute_url(self):
        return reverse_lazy('category', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    price = models.DecimalField(max_digits=8, decimal_places=2)
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    description = models.TextField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2,
                                           default=Decimal(0), validators=[validate_percent])
    picture = models.ImageField(upload_to='products')
    units_available = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    details_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    details_id = models.PositiveIntegerField()
    details_object = GenericForeignKey("details_content_type", "details_id")

    def __str__(self):
        return self.name

    objects = models.Manager()
    published = ProductManager()

    def get_absolute_url(self):
        return reverse_lazy('product', kwargs={'cat_slug': self.category.slug, 'id': self.pk})

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
