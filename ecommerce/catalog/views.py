from django.shortcuts import get_object_or_404
from django.views.generic import ListView

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
        return Product.published.filter(category_id=cat.pk).prefetch_related('details_object')
