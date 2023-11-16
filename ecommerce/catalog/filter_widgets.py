from abc import ABC, abstractmethod
import decimal
from decimal import Decimal
from typing import Optional, List, Mapping, Tuple
from enum import Enum, auto

from django.db.models import Model, QuerySet
from django.db.models import Max, Min
from django.http import QueryDict


class FilterWidget(ABC):
    """ Base class for filters.
    Filters parse GET-queries and filter QuerySets accordingly. Also can present itself using get_html method """
    @abstractmethod
    def __init__(self,
                 field: str,
                 queryset: QuerySet,
                 name: Optional[str] = None,
                 related_object: Optional[str] = None,
                 **kwargs):
        self.field = field
        self.related_object = related_object
        self.query_name = (self.related_object + '__' + self.field) if self.related_object else self.field
        if queryset is None:
            raise ValueError(f'No queryset provided for filter {repr(self)}')
        self.queryset = queryset.all()
        self.name = name if name else field

    @abstractmethod
    def parse(self, get_dict: Mapping[str, str]) -> None:
        pass

    @abstractmethod
    def filter(self, queryset: QuerySet) -> QuerySet:
        pass

    @abstractmethod
    def get_html(self):
        pass


class FilterBound(FilterWidget):
    def __init__(self,
                 field: str,
                 queryset: QuerySet,
                 **kwargs):
        super().__init__(field, queryset=queryset, **kwargs)

        bounds_dict = self.queryset.aggregate(min=Min(self.query_name), max=Max(self.query_name))
        self.lower_bound = bounds_dict['min']
        self.upper_bound = bounds_dict['max']

        self.min = self.lower_bound
        self.max = self.upper_bound

        self.GET_key_min = self.name + '_min'
        self.GET_key_max = self.name + '_max'

    @staticmethod
    def get_decimal_or_default(get_dict: Mapping[str, str], get_key: str, default: Decimal) -> Decimal:
        try:
            user_input = get_dict[get_key]
            return Decimal(user_input)
        # if get_key is not in get_dict or cannot be converted to Decimal return default
        except (KeyError, decimal.InvalidOperation):
            return default

    def parse(self, get_dict: Mapping[str, str]) -> None:
        self.max = min(self.get_decimal_or_default(get_dict, self.GET_key_max, self.max), self.upper_bound)
        self.min = max(self.get_decimal_or_default(get_dict, self.GET_key_min, self.min), self.lower_bound)

        if self.min > self.max:
            self.max = self.upper_bound
            self.min = self.lower_bound

    def filter(self, queryset: QuerySet) -> QuerySet:
        lookups = dict()
        if self.min != self.lower_bound:
            lookups[self.query_name + '__gte'] = self.min
        if self.max != self.upper_bound:
            lookups[self.query_name + '__lte'] = self.max
        return queryset.filter(**lookups)

    def get_html(self):
        return f'{self.name}: {self.lower_bound}-{self.upper_bound} | min {self.min}, max {self.max}'


class FilterChoicesWidget(FilterWidget):
    @abstractmethod
    def __init__(self,
                 field: str,
                 queryset: QuerySet,
                 **kwargs):
        super().__init__(field, queryset=queryset, **kwargs)
        # Note: using .distinct(field) is only allowed with PostgreSQL (unfortunately)
        self.choices = {str(option): False for option in self.queryset.values_list(self.query_name, flat=True)}
        self.show_all_choices = True
        self.GET_key = self.name

    def parse(self, get_dict: Mapping[str, str]) -> None:
        user_input = get_dict.get(self.GET_key)
        if user_input is None:
            return

        user_choices = user_input.split(',')
        for choice in user_choices:
            if choice in self.choices:
                self.choices[choice] = True
                self.show_all_choices = False

    def filter(self, queryset: QuerySet) -> QuerySet:
        if self.show_all_choices:
            return queryset

        user_choices = [choice for choice, show in self.choices.items() if show]
        lookup = dict()
        lookup[self.query_name + '__in'] = user_choices
        return queryset.filter(**lookup)

    def get_html(self):
        result = self.name + ': ' + ', '.join(self.choices.keys()) + ' | '
        if not self.show_all_choices:
            user_choices = []
            for key, show in self.choices.items():
                if show:
                    user_choices.append(key)
            result += ', '.join(user_choices)
        else:
            result += 'all'
        return result


class FilterDynamicChoices(FilterChoicesWidget):
    def __init__(self,
                 field: str,
                 queryset: QuerySet,
                 **kwargs):
        super().__init__(field, queryset=queryset, **kwargs)
        self.options = {str(option): False for option in self.queryset.values_list(self.query_name, flat=True)}


class FilterBoolChoices(FilterWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.GET_key = self.name
        self.choice: Optional[bool] = None

    def parse(self, get_dict: Mapping[str, str]) -> None:
        try:
            user_input = int(get_dict[self.GET_key])
        except (KeyError, ValueError):
            return  # use default
        if user_input == 1:
            self.choice = True
        elif user_input == 0:
            self.choice = False
        # else use default

    def filter(self, queryset: QuerySet) -> QuerySet:
        if self.choice is None:
            return queryset
        lookup = dict()
        lookup[self.query_name] = self.choice
        return queryset.filter(**lookup)

    def get_html(self):
        return f"{self.name}: True or False: { 'Any' if self.choice is None else self.choice }"


class FilterStaticChoices(FilterChoicesWidget):
    def __init__(self, field: str, queryset: QuerySet, choices: List[Tuple], **kwargs):
        """
        :param: choices is django-style choices of the field
        """
        super().__init__(field, queryset, **kwargs)
        self.choices = {key: False for key, _ in choices}


class FilterableMixin:
    FILTERS = []


class FilterWidgetFactory:
    class Filters(Enum):
        BOUND = auto()
        DYNAMIC_CHOICES = auto()
        BOOL_CHOICES = auto()
        STATIC_CHOICES = auto()

    _constructors = {
        Filters.BOUND: FilterBound,
        Filters.DYNAMIC_CHOICES: FilterDynamicChoices,
        Filters.BOOL_CHOICES: FilterBoolChoices,
        Filters.STATIC_CHOICES: FilterStaticChoices
    }

    def __call__(self, field: str,
                 filter_type: Filters,
                 queryset: QuerySet,
                 **kwargs):
        try:
            filter_constructor = self._constructors[filter_type]
        except KeyError:
            raise NotImplementedError(f"Filter type {filter_type} is not implemented")

        return filter_constructor(field, queryset=queryset, **kwargs)

    def add_filters_for_related_model(self,
                                      filters_list: List[FilterWidget],
                                      related_name: str,
                                      related_model: FilterableMixin,
                                      queryset: QuerySet):
        for field, filter_type in related_model.FILTERS:
            choices = None
            if filter_type == FilterWidgetFactory.Filters.STATIC_CHOICES:
                choices = related_model.__getattribute__(related_model, field).field.choices
            filters_list.append(self(field, filter_type, queryset, related_object=related_name, choices=choices))
