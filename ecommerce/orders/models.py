import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy

import catalog
from catalog.validators import validate_percent
from .validators import non_zero_validator


# Create your models here.


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    ship_to = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)

    products = models.ManyToManyField(catalog.models.Product,
                                      through='OrderProducts',
                                      through_fields=('order', 'product'))

    def get_absolute_url(self):
        return reverse_lazy('order', kwargs={'order_id': self.pk})


class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(catalog.models.Product, on_delete=models.PROTECT)

    buying_price = models.DecimalField(max_digits=8, decimal_places=2)
    buying_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_percent])
    amount = models.PositiveIntegerField(validators=[non_zero_validator])

    class Meta:
        constraints = [
            models.UniqueConstraint(name='unique_product_in_order', fields=['order', 'product'])
        ]
