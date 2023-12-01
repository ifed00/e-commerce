import json

from django import forms
from django.contrib.auth import get_user_model
from django.urls import path, reverse_lazy
from django.test import SimpleTestCase, override_settings, TestCase

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
