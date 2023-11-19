import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import make_aware

from catalog.models import Product, PhoneDetails, FridgeDetails, Category


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