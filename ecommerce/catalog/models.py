from decimal import Decimal

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


def validate_percent(input_data: Decimal) -> None:
    if input_data < 0 or input_data > 100:
        raise ValidationError(f'{input_data = }, but should be positive and less or equal to 100',
                              code = 'out_of_range')


class Product(models.Model):
    price = models.DecimalField(max_digits=8, decimal_places=2)
    name = models.CharField(max_length=255)
    description = models.TextField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_percent])
    picture = models.ImageField(upload_to='products')
    units_available = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    details_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    details_id = models.PositiveIntegerField()
    details_object = GenericForeignKey("details_content_type", "details_id")

    class Meta:
        indexes = [
            models.Index(fields=["details_content_type", "details_id"]),
        ]
