import random

from django import forms
from django.core.paginator import Paginator, EmptyPage
from django.db.models import QuerySet, F
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


from catalog.filters import FilterFactory, Filters
from catalog.models import Category, Product, BaseDetails
from catalog.search import SearchCategory, SearchCatalog
from integration_app.ajax_views_classes import AJAXPostView, AJAXAuthRequiredMixin

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


# AJAX-related views:

class ProductAmountForm(forms.Form):
    product_id = forms.ModelChoiceField(queryset=Product.published.all())
    amount = forms.IntegerField(required=False, min_value=1)


def get_payload_default():
    return {'amount': 1}


class AddProductToOrderView(AJAXAuthRequiredMixin, AJAXPostView):
    authentication_error_msg = 'anonymous users can not add products to basket'
    get_default = get_payload_default
    ValidationForm = ProductAmountForm

    def handle_request(self) -> None:
        product = self.cleaned_data['product_id']
        amount = self.cleaned_data['amount']

        if product.units_available < amount:
            self.response_data['error'] = 'requested amount is not available'
            self.status = 422
            return

        basket, _ = Order.baskets.get_or_create(user=self.request.user)

        detail, is_new = OrderProducts.objects.get_or_create(
            order=basket,
            product=product,
            defaults={
                'buying_price': product.price,
                'buying_discount_percent': product.discount_percent,
                'amount': amount
            })
        if not is_new:
            detail.amount = F('amount') + amount
            detail.save()

        product.units_available = F('units_available') - amount
        product.save()

        self.response_data['success'] = True


class DeleteProductFromOrderView(AJAXAuthRequiredMixin, AJAXPostView):
    authentication_error_msg = 'anonymous users can not delete products from basket'
    get_default = get_payload_default
    ValidationForm = ProductAmountForm

    def handle_request(self):
        product = self.cleaned_data['product_id']
        amount = self.cleaned_data['amount']

        try:
            basket = Order.baskets.get(user=self.request.user)
        except Order.DoesNotExist:
            self.status = 404
            self.response_data['error'] = 'no basket for the user exists'
            return

        try:
            detail = OrderProducts.objects.get(order=basket, product=product)
        except OrderProducts.DoesNotExist:
            self.status = 404
            self.response_data['error'] = 'no such product in the basket'
            return

        released_amount = min(detail.amount, amount)
        if detail.amount <= amount:
            detail.delete()
        else:
            detail.amount = F('amount') - amount
            detail.save()

        product.units_available = F('units_available') + released_amount
        product.save()

        self.response_data['success'] = True


class GetRandomProducts(View):
    def get(self, request, *args, **kwargs):
        try:
            page_num = int(request.GET.get('page', 1))
        except ValueError:
            return JsonResponse({}, status=400)

        if 'reset' in request.GET and 'seed' in request.session:
            del request.session['seed']

        seed = request.session.setdefault('seed', random.randint(-32568, 32568))

        ids = list(Product.published.values_list('pk', flat=True))
        random.seed(seed)
        random.shuffle(ids)

        paginated_ids = Paginator(ids, 10)

        try:
            current_page = paginated_ids.page(page_num)
        except EmptyPage:
            return JsonResponse({}, status=400)

        fields = ['pk', 'name', 'picture', 'category__name', 'category__slug']
        products = list(Product.published.filter(pk__in=current_page.object_list).values(*fields))

        return JsonResponse({'has_next_page': current_page.has_next(), 'products': products}, status=200)
