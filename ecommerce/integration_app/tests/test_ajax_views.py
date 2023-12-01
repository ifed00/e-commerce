import json

from django import forms
from django.contrib.auth import get_user_model
from django.urls import path, reverse_lazy, reverse
from django.test import SimpleTestCase, override_settings, TestCase

from catalog.models import Product
from catalog.tests.common_setup import common_setup
from orders.models import Order, OrderProducts
from ..ajax_views_classes import AJAXPostView, AJAXAuthRequiredMixin


@override_settings(ROOT_URLCONF='integration_app.tests.test_ajax_views')
class TestAJAXPostView(SimpleTestCase):
    def test_correct_request_produces_correct_response(self):
        res = self.client.post(reverse_lazy('ajax'),
                               {'name': 'MyNameIs', 'amount': 17},
                               content_type='application/json')

        answer = json.loads(res.content)
        self.assertTrue(answer['success'])
        self.assertEqual(res.status_code, 200)

    def test_incorrect_json_request_produces_400_status_code(self):
        res = self.client.post(reverse_lazy('ajax'),
                               "}",
                               content_type='application/json')

        answer = json.loads(res.content)

        self.assertFalse(answer['success'])
        self.assertIn('error', answer)
        self.assertEqual(res.status_code, 400)

    def test_incorrect_form_data_request_produces_400_status_code(self):
        res = self.client.post(reverse_lazy('ajax'),
                               {'name': 'MyNameIs', 'amount': -17},
                               content_type='application/json')

        answer = json.loads(res.content)

        self.assertFalse(answer['success'])
        self.assertIn('error', answer)
        self.assertEqual(res.status_code, 400)

    def test_request_missing_non_required_key_uses_default_and_produces_correct_response(self):
        res = self.client.post(reverse_lazy('ajax'),
                               {'name': 'MyNameIs'},
                               content_type='application/json')

        answer = json.loads(res.content)
        self.assertTrue(answer['success'])
        self.assertEqual(answer['cleaned_data']['amount'], 66)
        self.assertEqual(res.status_code, 200)

    def test_request_missing_required_key_produces_400_status_code(self):
        res = self.client.post(reverse_lazy('ajax'),
                               {'amount': 12},
                               content_type='application/json')

        answer = json.loads(res.content)
        self.assertFalse(answer['success'])
        self.assertEqual(res.status_code, 400)


@override_settings(ROOT_URLCONF='integration_app.tests.test_ajax_views')
class TestAJAXAuthenticationMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(username='Me', password='111')

    def test_unauthenticated_access_is_Forbidden(self):
        res = self.client.post(reverse_lazy('auth_req_ajax'),
                               {'name': 'MyNameIs', 'amount': 12},
                               content_type='application/json')

        answer = json.loads(res.content)
        self.assertFalse(answer['success'])
        self.assertEqual(res.status_code, 403)

    def test_authenticated_access_is_OK(self):
        self.client.force_login(self.user)

        res = self.client.post(reverse_lazy('auth_req_ajax'),
                               {'name': 'MyNameIs', 'amount': 12},
                               content_type='application/json')

        answer = json.loads(res.content)
        self.assertTrue(answer['success'])
        self.assertEqual(answer['cleaned_data']['name'], 'MyNameIs')
        self.assertEqual(answer['cleaned_data']['amount'], 12)
        self.assertEqual(res.status_code, 200)


class NameAmountForm(forms.Form):
    name = forms.CharField(max_length=16)
    amount = forms.IntegerField(required=False, min_value=1)


def get_default_values():
    return {'amount': 66}


class ExampleForTestAJAXView(AJAXPostView):
    get_default = get_default_values
    ValidationForm = NameAmountForm

    def handle_request(self) -> None:
        self.response_data['success'] = True
        self.response_data['cleaned_data'] = self.cleaned_data


class ExampleForTestMixinView(AJAXAuthRequiredMixin, ExampleForTestAJAXView):
    authentication_error_msg = 'my custom message forbidden'


urlpatterns = [
    path('test/ajax', ExampleForTestAJAXView.as_view(), name='ajax'),
    path('test/auth/ajax', ExampleForTestMixinView.as_view(), name='auth_req_ajax')
]


class TestAddProductToOrderView(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)
        cls.user = get_user_model().objects.create(username='Mia', password='Ami')

    def setUp(self):
        self.client.force_login(self.user)

    def test_correct_request_updates_existing_OrderProducts_entry(self):
        basket = Order.objects.create(user=self.user)  # creating basket to ensure its existence
        product_id = 1
        buy_entry = OrderProducts.objects.create(order=basket,
                                                 product_id=product_id,
                                                 buying_price=100,
                                                 buying_discount_percent=0,
                                                 amount=1)

        self.client.post(reverse('order_add'),
                         {'product_id': product_id, 'amount': 2},
                         content_type='application/json')

        buy_entry.refresh_from_db()
        self.assertEqual(basket.products.filter(pk=product_id).count(), 1)
        self.assertEqual(buy_entry.amount, 3)

        # doesn't change:
        self.assertEqual(buy_entry.buying_price, 100)
        self.assertEqual(buy_entry.buying_discount_percent, 0)

    def test_correct_request_creates_OrderProducts_entry_if_no_such_exists_using_Product_data(self):
        basket = Order.objects.create(user=self.user)  # creating basket to ensure its existence
        product_id = 1

        self.client.post(reverse('order_add'),
                         {'product_id': product_id, 'amount': 2},
                         content_type='application/json')

        self.assertEqual(basket.products.filter(pk=product_id).count(), 1)
        buy_entry = OrderProducts.objects.get(order=basket, product_id=product_id)
        self.assertEqual(buy_entry.amount, 2)

        # using Product data:
        product = Product.published.get(pk=product_id)
        self.assertEqual(buy_entry.buying_price, product.price)
        self.assertEqual(buy_entry.buying_discount_percent, product.discount_percent)

    def test_correct_request_creates_Order_as_basket_if_no_such_exists(self):
        product_id = 1

        self.client.post(reverse('order_add'),
                         {'product_id': product_id, 'amount': 2},
                         content_type='application/json')

        self.assertEqual(Order.baskets.filter(user=self.user).count(), 1)

    def test_missing_amount_key_uses_1_as_default(self):
        basket = Order.objects.create(user=self.user)  # creating basket to ensure its existence

        product_id = 3

        self.client.post(reverse('order_add'),
                         {'product_id': product_id},
                         content_type='application/json')

        buy_entry = OrderProducts.objects.get(order=basket, product_id=product_id)
        self.assertEqual(buy_entry.amount, 1)

    def test_requesting_too_much_amount_produces_422_status_code_and_doesnt_change_state(self):
        product_id = 2

        response = self.client.post(reverse('order_add'),
                                    {'product_id': product_id, 'amount': 300000},
                                    content_type='application/json')

        answer = json.loads(response.content)
        self.assertFalse(answer['success'])
        self.assertEqual(response.status_code, 422)
        self.assertIn('error', answer)

        self.assertEqual(Order.baskets.filter(user=self.user).count(), 0)

    def test_correct_request_updates_corresponding_Product_entry(self):
        product_id = 4
        amount_before_request = Product.published.get(pk=product_id).units_available

        self.client.post(reverse('order_add'),
                         {'product_id': product_id, 'amount': 2},
                         content_type='application/json')

        amount_after_request = Product.published.get(pk=product_id).units_available

        self.assertEqual(amount_after_request + 2, amount_before_request)

