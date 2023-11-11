from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum, auto

from django.db.models import Model, QuerySet
from django.db.models import Max, Min


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
        self.queryset = queryset
        self.name = kwargs.get('name', field)

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

    def get_html(self):
        return f'{self.name}: {self.lower_bound}-{self.upper_bound}'


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
