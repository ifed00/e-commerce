from typing import List, Tuple, Dict

from django.db.models import Q, QuerySet, Count, Model


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
    def __init__(self, fields: List[str], category_model: type[Model], show_first: int = 5):
        self.fields = fields
        self.category_model = category_model
        self.first_found_products: Dict[str, List[Model]] = dict()
        self.show_first = show_first

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

        products = queryset.filter(result_query)

        cats_list = products.values('category').annotate(found=Count('category'))

        cat_ids = [cat['category'] for cat in cats_list]

        queryset = self.category_model.objects.filter(pk__in=cat_ids)

        self.first_found_products = {cat['category']: list() for cat in cats_list}

        for p in products:
            cat = p.category_id
            pre_list = self.first_found_products[cat]
            if len(pre_list) > self.show_first:
                continue

            pre_list.append(p)

        return queryset
