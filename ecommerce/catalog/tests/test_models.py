import datetime
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from catalog.models import Product, Category

from catalog_test_app.models import PhoneDetails


class PublishedManager(TestCase):
    def setUp(self):
        self.phone_cat = Category.objects.create(
            name='phones',
            slug='phones',
            details_content_type=ContentType.objects.get_for_model(PhoneDetails)
        )
        self.details_index = -1
        self.available_details = [
            PhoneDetails.objects.create(
                color='red',
                memory_KB=2048 * 1024,
                display_resolution='980x620',
                camera_resolution='990x280'
            ),
            PhoneDetails.objects.create(
                color='purple',
                memory_KB=1042 * 1024,
                display_resolution='1980x720',
                camera_resolution='600x600'
            ),
            PhoneDetails.objects.create(
                color='blue',
                memory_KB=512 * 1024,
                display_resolution='1020x1020',
                camera_resolution='870x780')
        ]

    def create_test_product(self, published_at: datetime.datetime) -> Product:
        self.details_index += 1
        return Product.objects.create(
            name='p' + str(self.details_index),
            price=18050,
            manufacturer='Shansung',
            description='test description',
            discount_percent=0,
            units_available=1,
            category=self.phone_cat,
            details_object=self.available_details[self.details_index],
            published_at=published_at
        )

    def test_published_products_returned(self):
        now = timezone.now()
        p1 = self.create_test_product(published_at=now - timedelta(days=1))
        p2 = self.create_test_product(published_at=now - timedelta(weeks=1, hours=6))
        p3 = self.create_test_product(published_at=now)

        result = Product.published.all()

        self.assertEqual(len(result), 3)
        result_list = list(result)
        self.assertTrue(p1 in result_list)
        self.assertTrue(p2 in result_list)
        self.assertTrue(p3 in result_list)

    def test_not_published_products_not_returned(self):
        now = timezone.now()

        p1 = self.create_test_product(published_at=now + timedelta(minutes=5))
        p2 = self.create_test_product(published_at=now - timedelta(minutes=5))

        result = Product.published.all()

        self.assertEqual(len(result), 1)
        result_list = list(result)
        self.assertTrue(p2 in result_list)

        self.assertFalse(p1 in result_list)

