from abc import ABC, abstractmethod
import decimal
from decimal import Decimal
from typing import Optional, List, Mapping, Tuple, Dict
from enum import Enum, auto

from django.db.models import QuerySet
from django.db.models import Max, Min


class FilterableMixin:
    FILTERS = []


class Filters(Enum):
    BOUND = auto()
    DYNAMIC_CHOICES = auto()
    BOOL_CHOICES = auto()
    STATIC_CHOICES = auto()


class FilterBase(ABC):
    """ Base class for filters.
    Filters parse GET-queries and filter QuerySets accordingly. Also can present itself using get_html method """
    @abstractmethod
    def __init__(self, field: str, *, name: Optional[str] = None, query_to: Optional[str] = None, **kwargs):
        """
        :param field: field to filter by
        :param name: name for filter, usually used as GET key
        :param query_to: name of the related model with provided field
        """
        self.field = field
        self.query_name = (query_to + '__' + self.field) if query_to else self.field
        self.name = name if name else field

    @abstractmethod
    def parse(self, query_dict: Mapping[str, str]) -> None:
        """ Parses GET or POST query_dict looking for filter-specific keys """
        pass

    @abstractmethod
    def filter(self, queryset: QuerySet) -> QuerySet:
        """ Narrows provided QuerySet """
        pass

    @abstractmethod
    def get_html(self) -> str:
        """ Returns html to show widget, use in templates """
        pass


# Utility function
def get_decimal(from_mapping: Mapping[str, str], key: str, default: Decimal) -> Decimal:
    """ If key is not in from_mapping or cannot be converted to Decimal returns default"""
    try:
        user_input = from_mapping[key]
        return Decimal(user_input)
    except (KeyError, decimal.InvalidOperation):
        return default


class FilterBound(FilterBase):
    """ Filters by numeric field, checking whether it is in provided range.
    Available range is determined dynamically by a request to DB """
    def __init__(self, field: str, queryset: QuerySet, **kwargs):
        super().__init__(field, queryset=queryset, **kwargs)

        bounds_dict = queryset.aggregate(min=Min(self.query_name), max=Max(self.query_name))
        self.lower_bound = bounds_dict['min']
        self.upper_bound = bounds_dict['max']

        self.min = self.lower_bound
        self.max = self.upper_bound

        self.GET_key_min = self.name + '_min'
        self.GET_key_max = self.name + '_max'

    def parse(self, query_dict: Mapping[str, str]) -> None:
        self.max = min(get_decimal(query_dict, self.GET_key_max, self.max), self.upper_bound)
        self.min = max(get_decimal(query_dict, self.GET_key_min, self.min), self.lower_bound)

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


class FilterChoicesBase(FilterBase):
    """ Base class for choices filters
        Provided multiple variants returns objects with any of these variants
    """
    @abstractmethod
    def __init__(self, field: str, **kwargs):
        super().__init__(field, **kwargs)

        self.show_all_choices = True
        self.GET_key = self.name

        self.choices: Dict[str, bool] = None  # Note: set self.choices in concrete's class __init__

    def parse(self, query_dict: Mapping[str, str]) -> None:
        user_input = query_dict.get(self.GET_key)
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


class FilterDynamicChoices(FilterChoicesBase):
    """ Filters by field with arbitrary variants (e.g. manufacturer), available variants determined by DB request """
    def __init__(self, field: str, queryset: QuerySet, **kwargs):
        super().__init__(field, **kwargs)
        self.choices = {str(choice): False for choice in queryset.values_list(self.query_name, flat=True)}


class FilterBool(FilterBase):
    """ Filters by BooleanField """
    def __init__(self, field: str, **kwargs):
        super().__init__(field, **kwargs)
        self.GET_key = self.name
        self.choice: Optional[bool] = None

    def parse(self, query_dict: Mapping[str, str]) -> None:
        try:
            user_input = int(query_dict[self.GET_key])
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


class FilterStaticChoices(FilterChoicesBase):
    """ Filters by static set of variants (e.g. django Field with choices attribute set)"""
    def __init__(self, field: str, choices: List[Tuple], **kwargs):
        """
        :param: choices - django-style choices of the field
        """
        super().__init__(field, **kwargs)
        self.choices = {key: False for key, _ in choices}


class FilterFactory:
    _constructors = {
        Filters.BOUND: FilterBound,
        Filters.DYNAMIC_CHOICES: FilterDynamicChoices,
        Filters.BOOL_CHOICES: FilterBool,
        Filters.STATIC_CHOICES: FilterStaticChoices
    }

    @classmethod
    def produce(cls, field: str, filter_type: Filters, queryset: QuerySet, **kwargs):
        try:
            filter_constructor = cls._constructors[filter_type]
        except KeyError:
            raise NotImplementedError(f"Filter type {filter_type} is not implemented")

        return filter_constructor(field, queryset=queryset, **kwargs)

    @classmethod
    def add_filters_for_related_model(cls, filters_list: List[FilterBase], related_name: str,
                                      related_model: type[FilterableMixin], queryset: QuerySet):
        """ Parses Django model with FilterableMixin, produces filters and adds them to filter_list """
        for field, filter_type in related_model.FILTERS:
            choices = None
            if filter_type == Filters.STATIC_CHOICES:
                choices = related_model.__getattribute__(related_model, field).field.choices

            filters_list.append(
                cls.produce(field, filter_type, queryset, query_to=related_name, choices=choices)
            )
