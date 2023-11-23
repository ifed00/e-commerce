from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


from catalog.filters import FilterFactory, Filters
from catalog.models import Category, Product, BaseDetails
from catalog.search import SearchCategory, SearchCatalog

from orders.models import Order, OrderProducts


# Create your views here.

# Catalog related views:


class IndexView(ListView):
    queryset = Category.objects.all()
    template_name = 'catalog/index_page.html'
    context_object_name = 'categories'


class CategoryView(ListView):
    template_name = 'catalog/category_index.html'
    context_object_name = 'products'

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        queryset = Product.published.filter(category_id=category.pk)\
            .prefetch_related('category').prefetch_related('details_object')

        # gather first because dynamic filters need access to unfiltered queryset
        self.gather_filters(queryset, category.details_content_type.model_class())

        queryset = self.apply_filters(queryset)

        if 'q' in self.request.GET:
            search_engine = SearchCategory(['name'])
            queryset = search_engine.filter(self.request.GET['q'], queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_widgets'] = self.filters
        return context

    def gather_filters(self, queryset: QuerySet, related_model_class: type[BaseDetails]):
        self.filters = [
            FilterFactory.produce('price', Filters.BOUND, queryset=queryset),
            FilterFactory.produce('manufacturer', Filters.DYNAMIC_CHOICES, queryset=queryset)
        ]

        FilterFactory.add_filters_for_related_model(self.filters,
                                                    related_model_class.generic_relation_name,
                                                    related_model_class,
                                                    queryset)

        for f in self.filters:
            f.parse(self.request.GET)

    def apply_filters(self, queryset: QuerySet) -> QuerySet:
        result = queryset
        for f in self.filters:
            result = f.filter(result)
        return result


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


class SearchView(ListView):
    template_name = 'catalog/search_results.html'
    context_object_name = 'categories'

    def get_queryset(self):
        if 'q' not in self.request.GET:
            raise ValueError('Bad request')
        user_query = self.request.GET['q']

        search_engine = SearchCatalog(['name', 'category__name'])
        search_results = search_engine.filter(user_query, Product.published.all().prefetch_related('category'))

        return search_results

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['query'] = 'q=' + self.request.GET['q']
        return context


# Orders related views:

class OrderView(LoginRequiredMixin, ListView):
    template_name = 'orders/order.html'
    context_object_name = 'product_details'

    def get_queryset(self):
        order = get_object_or_404(Order, pk=self.kwargs['order_id'])

        self.order = order

        if self.order.user.id != self.request.user.id:
            raise PermissionDenied

        return OrderProducts.objects.filter(order=order).select_related('product')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(objects_list=object_list, **kwargs)

        context['order'] = self.order

        return context


class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'profile.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)