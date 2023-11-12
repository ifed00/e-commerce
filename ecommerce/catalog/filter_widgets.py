from abc import ABC, abstractmethod
import decimal
from decimal import Decimal
from typing import Optional
from enum import Enum, auto

from django.db.models import Model, QuerySet
from django.db.models import Max, Min
from django.http import QueryDict


class FilterWidget(ABC):
    @abstractmethod
    def __init__(self, model: Model, field: str,
                 *,
                 queryset: Optional[QuerySet] = None,
                 **kwargs):
        self.model = model
        self.field = field
        if queryset is None:
            queryset = self.model._base_manager.all()
        self.queryset = queryset.all()
        self.name = kwargs.get('name', field)

    @abstractmethod
    def parse(self, get_dict) -> None:
        pass

    @abstractmethod
    def get_html(self):
        pass


class FilterBound(FilterWidget):
    def __init__(self, model: Model, field: str,
                 *,
                 queryset: Optional[QuerySet] = None,
                 **kwargs):
        super().__init__(model, field, queryset=queryset, **kwargs)

        bounds_dict = self.queryset.aggregate(min=Min(field), max=Max(field))
        self.lower_bound = bounds_dict['min']
        self.upper_bound = bounds_dict['max']

        self.min = self.lower_bound
        self.max = self.upper_bound

        self.GET_key_min = self.name + '_min'
        self.GET_key_max = self.name + '_max'

    def parse(self, get_dict: QueryDict) -> None:
        # TODO: refactor!!!
        try:
            self.max = min(Decimal(get_dict.get(self.GET_key_max, self.max)), self.upper_bound)
        except decimal.InvalidOperation:  # if GET key cannot be converted to Decimal use default (do nothing)
            pass
        try:
            self.min = max(Decimal(get_dict.get(self.GET_key_min, self.min)), self.lower_bound)
        except decimal.InvalidOperation:  # if GET key cannot be converted to Decimal use default (do nothing)
            pass

        if self.min > self.max:
            self.max = self.upper_bound
            self.min = self.lower_bound

    def get_html(self):
        return f'{self.name}: {self.lower_bound}-{self.upper_bound} | min {self.min}, max {self.max}'


class FilterWidgetFactory:
    class Filters(Enum):
        BOUND = auto()

    def __call__(self, model: Model,
                 field: str,
                 filter_type: Filters,
                 *,
                 queryset: Optional[QuerySet] = None,
                 **kwargs):
        match filter_type:
            case self.Filters.BOUND:
                return FilterBound(model, field, queryset=queryset, **kwargs)
            case _:
                raise NotImplementedError
