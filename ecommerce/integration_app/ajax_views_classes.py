import json
from json import JSONDecodeError
from typing import Dict, Callable

from django import forms
from django.http import JsonResponse
from django.views import View


class AJAXPostView(View):
    get_default: Callable[[], Dict]
    ValidationForm: type[forms.Form]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.response_data = {'success': False}
        self.cleaned_data = None
        self.payload = self.__class__.get_default()
        self.status = 200

    def post(self, request, *args, **kwargs):
        if self.parse_request():
            self.handle_request()

        return JsonResponse(self.response_data, status=self.status)

    def handle_request(self) -> None:
        pass

    def parse_request(self) -> bool:
        try:
            self.payload.update(json.loads(self.request.body))
        except JSONDecodeError:
            self.response_data['error'] = 'request malformed: use JSON format'
            self.status = 400
            return False

        data = self.ValidationForm(self.payload)

        if not data.is_valid():
            self.response_data['error'] = data.errors
            self.status = 400
            return False

        self.cleaned_data = data.cleaned_data

        return True


class AJAXAuthRequiredMixin:
    authentication_error_msg = 'Forbidden'

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            self.response_data['error'] = self.authentication_error_msg
            self.status = 403

            return JsonResponse(self.response_data, status=self.status)

        return super().post(request, *args, **kwargs)
