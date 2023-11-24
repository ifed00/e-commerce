import json
from json import JSONDecodeError

from django.db.models import QuerySet, F
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
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
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        queryset = Product.published.filter(category_id=self.category.pk)\
            .prefetch_related('category').prefetch_related('details_object')

        # gather first because dynamic filters need access to unfiltered queryset
        self.gather_filters(queryset, self.category.details_content_type.model_class())

        queryset = self.apply_filters(queryset)

        if 'q' in self.request.GET:
            search_engine = SearchCategory(['name'])
            queryset = search_engine.filter(self.request.GET['q'], queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_widgets'] = self.filters
        context['current_category'] = self.category
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


class AddProductToOrderView(View):
    def post(self, request, *args, **kwargs):
        response_data = {'success': False}
        if not request.user.is_authenticated:
            response_data['error'] = 'anonymous users can not add products to basket'
            return JsonResponse(response_data, status=403)

        try:
            payload = json.loads(request.body)
            product_id = payload['product_id']
        except (KeyError, JSONDecodeError):
            response_data['error'] = 'request malformed: use JSON format and provide product_id key'
            return JsonResponse(response_data, status=400)

        try:
            product = Product.published.get(pk=product_id)
        except Product.DoesNotExist:
            response_data['error'] = f'product {product_id} not found'
            return JsonResponse(response_data, status=404)

        try:
            basket = Order.baskets.get(user=request.user)
        except Order.DoesNotExist:
            basket = Order.objects.create(user=request.user)

        amount = payload.get('amount', 1)

        if product.units_available < amount:
            response_data['error'] = 'requested amount is not available'
            return JsonResponse(response_data, status=422)

        try:
            detail = OrderProducts.objects.filter(order=basket, product=product).get()
            detail.amount = F('amount') + amount
            detail.save()
        except OrderProducts.DoesNotExist:
            OrderProducts.objects.create(
                order=basket,
                product=product,
                buying_price=product.price,
                buying_discount_percent=product.discount_percent,
                amount=amount
            )

        product.units_available = F('units_available') - amount
        product.save()

        response_data['success'] = True
        return JsonResponse(response_data, status=200)
