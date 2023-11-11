from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from .filter_widgets import FilterWidgetFactory
from .models import Category, Product

# Create your views here.


class IndexView(ListView):
    queryset = Category.objects.all()
    template_name = 'catalog/index_page.html'
    context_object_name = 'categories'


class CategoryView(ListView):  # TODO: add filter products feature
    template_name = 'catalog/category_index.html'
    context_object_name = 'products'

    def get_queryset(self):
        cat = get_object_or_404(Category, slug=self.kwargs['slug'])
        self.products = Product.published.filter(category_id=cat.pk).prefetch_related('details_object')
        return self.products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factory = FilterWidgetFactory()
        context['filter_widgets'] = []
        context['filter_widgets'].append(
            factory(Product,
                    'price',
                    FilterWidgetFactory.Filters.BOUND,
                    queryset=self.products,
                    name='Price')
        )
        return context
