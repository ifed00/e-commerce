from typing import List

from django.db.models import Q, QuerySet, Count


class SearchCategory:
    def __init__(self, fields: List[str]):
        self.fields = fields

    def filter(self, query: str, queryset: QuerySet) -> QuerySet:
        if not query:
            return queryset
        tokens = query.split()
        result_query = Q()
        for token in tokens:
            for field in self.fields:
                lookup = dict()
                lookup[field + '__icontains'] = token
                result_query = result_query | Q(**lookup)

        return queryset.filter(result_query)


class SearchCatalog:
    def __init__(self, fields: List[str]):
        self.fields = fields

    def filter(self, query: str, queryset: QuerySet) -> QuerySet:
        if not query:
            return queryset
        tokens = query.split()
        result_query = Q()

        for token in tokens:
            for field in self.fields:
                lookup = dict()
                lookup[field + '__icontains'] = token
                result_query = result_query | Q(**lookup)

        queryset = queryset.filter(result_query).annotate(found=Count('product'))

        return queryset
