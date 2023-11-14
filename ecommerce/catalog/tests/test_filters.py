import datetime

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import make_aware

from catalog.models import Product, PhoneDetails, FridgeDetails, Category
from catalog.filter_widgets import FilterBound


def common_setup(cls):
    """ unittest feature setUpModule is not supported by django so common data setup is provided here.
        Call in TestCase.setUpTestData method.
    """

    cls.available_categories = [
        Category.objects.create(
            name='phones',
            slug='phones',
            details_content_type=ContentType.objects.get_for_model(PhoneDetails)
        ),
        Category.objects.create(
            name='fridges',
            slug='fridges',
            details_content_type=ContentType.objects.get_for_model(FridgeDetails)
        )
    ]

    cls.available_details = [
        PhoneDetails.objects.create(
            color='red',
            memory_KB=2097152,  # 2Gb
            display_resolution='980x620',
            camera_resolution='990x280'
        ),
        PhoneDetails.objects.create(
            color='purple',
            memory_KB=1048576,  # 1Gb
            display_resolution='1980x720',
            camera_resolution='600x600'
        ),
        PhoneDetails.objects.create(
            color='blue',
            memory_KB=524288,  # 500Mb
            display_resolution='1020x1020',
            camera_resolution='870x780'
        ),
        FridgeDetails.objects.create(
            volume_liters=80,
            has_freezer=False,
            color='black',
            EU_energy_label='A'
        ),
        FridgeDetails.objects.create(
            volume_liters=380,
            has_freezer=True,
            color='white',
            EU_energy_label='A++'
        ),
        FridgeDetails.objects.create(
            volume_liters=200,
            has_freezer=True,
            color='white',
            EU_energy_label='B'
        )
    ]

    cls.available_products = [
        Product.objects.create(
            name='Galaxy W',
            price=28500,
            manufacturer='Shansung',
            description='test description',
            discount_percent=0,
            units_available=100,
            category=cls.available_categories[0],
            details_object=cls.available_details[0],
            published_at=make_aware(datetime.datetime(2020, 10, 13))
        ),
        Product.objects.create(
            name='Erick Son',
            price=40000,
            manufacturer='Bony',
            description='Test description',
            discount_percent=0,
            units_available=70,
            category=cls.available_categories[0],
            details_object=cls.available_details[1],
            published_at=make_aware(datetime.datetime(2020, 10, 16))
        ),
        Product.objects.create(
            name='iCall 99',
            price=85000,
            manufacturer='Banana',
            description='Best ergonomics in the world',
            discount_percent=0,
            units_available=250,
            category=cls.available_categories[0],
            details_object=cls.available_details[2],
            published_at=make_aware(datetime.datetime(2020, 10, 18))
        ),
        Product.objects.create(
            name='Freeze One',
            price=78500,
            manufacturer='POSH',
            description='Cool as heart of that girl',
            discount_percent=0,
            units_available=10,
            category=cls.available_categories[1],
            details_object=cls.available_details[3],
            published_at=make_aware(datetime.datetime(2020, 9, 8))
        ),
        Product.objects.create(
            name='M8690',
            price=186900,
            manufacturer='Homestead',
            description='Best for your family and kids!',
            discount_percent=0,
            units_available=17,
            category=cls.available_categories[1],
            details_object=cls.available_details[4],
            published_at=make_aware(datetime.datetime(2020, 9, 27))
        ),
        Product.objects.create(
            name="Loner's Choice",
            price=32999,
            manufacturer='Sentinel',
            description='Keeps your beer cool, that is what you asked.',
            discount_percent=0,
            units_available=3,
            category=cls.available_categories[1],
            details_object=cls.available_details[5],
            published_at=make_aware(datetime.datetime(2020, 9, 22))
        )
    ]


class TestFilterBound(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def test_filtering_by_min_works_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='100000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.available_products[4])

    def test_filtering_by_max_works_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_max='35000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[0] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_filtering_by_min_and_max_works_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='60000', price_max='100000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[2] in result)
        self.assertTrue(self.available_products[3] in result)

    def test_min_above_max_removes_bounds_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='100001', price_max='100000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 6)
    
    def test_min_below_minimal_removes_min_and_preserves_max(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='28499', price_max='35000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[0] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_max_above_maximal_removes_max_and_preserves_min(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='80000', price_max='200000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[2] in result)
        self.assertTrue(self.available_products[4] in result)

    def test_none_decimal_GET_value_ignored(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='80000', price_max='reasonable')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[2] in result)
        self.assertTrue(self.available_products[4] in result)

    def test_GET_keys_missing_produces_no_filtering(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_bad_key='100001', max_price='100000')  # Note: wrong GET keys provided

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 6)

    def test_filtering_on_related_model_works_correctly(self):
        category_phones = self.available_categories[0]
        qs = Product.objects.filter(category_id=category_phones.pk)

        related_object_name = category_phones.details_content_type.model_class().generic_relation_name

        test_filter = FilterBound('memory_KB', qs, related_object=related_object_name)
        mem_750mb = '786432'
        mem_1250mb = '1310720'
        GET_dict = dict(memory_KB_min=mem_750mb, memory_KB_max=mem_1250mb)

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertTrue(self.available_products[1] in result)

    def test_providing_name_changes_GET_key_names(self):
        category_phones = self.available_categories[0]
        qs = Product.objects.filter(category_id=category_phones.pk)

        related_object_name = category_phones.details_content_type.model_class().generic_relation_name

        test_filter = FilterBound('memory_KB', qs, name='mem', related_object=related_object_name)
        mem_750mb = '786432'
        mem_1250mb = '1310720'
        GET_dict = dict(mem_min=mem_750mb, mem_max=mem_1250mb)

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertTrue(self.available_products[1] in result)

