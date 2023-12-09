from dataclasses import dataclass
from typing import List, Dict

from django.db.models import Q, QuerySet, Count, Case, When, Value

from catalog.models import Product, Category


def make_Q(field: str, token: str) -> Q:
    lookup = dict()
    lookup[field + '__icontains'] = token
    return Q(**lookup)


class SearchBase:
    def __init__(self, fields: List[str]):
        self.fields = fields

    def _filter(self, query: str, queryset: QuerySet) -> QuerySet:
        tokens = query.split()
        result_Q = Q()
        for token in tokens:
            for field in self.fields:
                result_Q = result_Q | make_Q(field, token)

        return queryset.filter(result_Q)


class SearchCategory(SearchBase):
    def filter(self, query: str, queryset: QuerySet) -> QuerySet:
        if not query:
            return queryset
        return super()._filter(query, queryset)


class SearchCatalog:
    class NoQuerySpecified(Exception):
        pass

    def __init__(self, show_first: int = 3):
        self.show_first = show_first

    @dataclass
    class SearchResultInfo:
        category: Category
        found: int
        first_found_products: List[Product]  # len <= show_first
        whole_category: bool

    def filter(self, query: str) -> List[SearchResultInfo]:
        if not query:
            raise self.NoQuerySpecified()

        tokens = query.split()
        result_Q = Q()
        for token in tokens:
            result_Q = result_Q | make_Q('name', token)

        categories = Category.objects.annotate(whole_match=Case(When(result_Q, then=Value(1)), default=Value(0)))

        search_results = list()
        for c in categories:
            if c.whole_match:
                qs = c.product_set.all()
            else:
                qs = c.product_set.filter(result_Q)

            found = qs.count()

            if found != 0:
                first_products = list(qs[:self.show_first])

                search_results.append(
                    self.SearchResultInfo(
                        category=c,
                        found=found,
                        first_found_products=first_products,
                        whole_category=c.whole_match
                    )
                )

        return search_results
