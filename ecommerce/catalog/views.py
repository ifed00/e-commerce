from typing import List

from django.db.models import Q, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from .filter_widgets import FilterFactory, Filters
from .models import Category, Product

# Create your views here.


class IndexView(ListView):
    queryset = Category.objects.all()
    template_name = 'catalog/index_page.html'
    context_object_name = 'categories'


class CategoryView(ListView):  # TODO: add filter products feature
    template_name = 'catalog/category_index.html'
    context_object_name = 'products'

    def pre_get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.published.filter(category_id=self.category.pk).prefetch_related('details_object')

    def get_queryset(self):
        return self.objects_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_widgets'] = self.filters
        return context

    def gather_filters(self):
        self.filters = [
            FilterFactory.produce('price', Filters.BOUND, queryset=self.objects_list),
            FilterFactory.produce('manufacturer', Filters.DYNAMIC_CHOICES, queryset=self.objects_list)
        ]

        related_model_class = self.category.details_content_type.model_class()
        FilterFactory.add_filters_for_related_model(self.filters,
                                                    related_model_class.generic_relation_name,
                                                    related_model_class,
                                                    self.objects_list)

        for f in self.filters:
            f.parse(self.request.GET)

    def apply_filters(self):
        for f in self.filters:
            self.objects_list = f.filter(self.objects_list)

    def get(self, request, *args, **kwargs):
        self.objects_list = self.pre_get_queryset()

        self.gather_filters()  # gather first because dynamic filters need access to unfiltered queryset
        self.apply_filters()

        return super().get(request, *args, **kwargs)


class ProductView(DetailView):
    template_name = 'catalog/product_details.html'
    pk_url_kwarg = 'id'
    context_object_name = 'product'
    queryset = Product.published.all()

    def get_object(self, queryset=None):
        product = super().get_object()

        category = get_object_or_404(Category, slug=self.kwargs['cat_slug'])

        if product.category_id != category.pk:
            raise Http404("Wrong category used!")

        return product

    def get_context_data(self, **kwargs):
        return super().get_context_data(details=self.object.details_object)


class SearchCategory:
    def __init__(self, fields: List[str]):
        self.fields = fields

    def filter(self, query: str, queryset: QuerySet) -> QuerySet:
        tokens = query.split()
        result_query = Q()
        for token in tokens:
            for field in self.fields:
                lookup = dict()
                lookup[field + '__icontains'] = token
                result_query = result_query | Q(**lookup)

        return queryset.filter(result_query)
