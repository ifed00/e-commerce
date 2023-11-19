from dataclasses import dataclass
from typing import List, Dict

from django.db.models import Q, QuerySet, Count

from catalog.models import Product, Category


class SearchBase:
    def __init__(self, fields: List[str]):
        self.fields = fields

    def _filter(self, query: str, queryset: QuerySet) -> QuerySet:
        tokens = query.split()
        result_query = Q()
        for token in tokens:
            for field in self.fields:
                lookup = dict()
                lookup[field + '__icontains'] = token
                result_query = result_query | Q(**lookup)

        return queryset.filter(result_query)


class SearchCategory(SearchBase):
    def filter(self, query: str, queryset: QuerySet) -> QuerySet:
        if not query:
            return queryset
        return super()._filter(query, queryset)


class SearchCatalog(SearchBase):
    class NoQuerySpecified(Exception):
        pass

    def __init__(self, fields: List[str], show_first: int = 3):
        super().__init__(fields)
        self.show_first = show_first

    @dataclass
    class SearchResultInfo:
        category: Category
        found: int
        first_found_products: List[Product]  # len <= show_first

    def filter(self, query: str, products: QuerySet) -> List[SearchResultInfo]:
        if not query:
            raise self.NoQuerySpecified()

        # following code highly relies on this QuerySet being sorted by category_id
        products = super()._filter(query, products).order_by('category_id')

        search_results = list(products.values('category').annotate(found=Count('category')))

        prev_cat_id = -1
        results_index = -1
        single_result = None
        for p in products:
            cat_id = p.category_id
            if prev_cat_id != cat_id:
                prev_cat_id = cat_id
                results_index += 1
                single_result = search_results[results_index]
                single_result['category'] = p.category
                single_result['first_found_products'] = list()

            if len(single_result['first_found_products']) < self.show_first:
                single_result['first_found_products'].append(p)

        return [self.SearchResultInfo(**r) for r in search_results]
