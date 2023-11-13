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

    def pre_get_queryset(self):
        cat = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.published.filter(category_id=cat.pk).prefetch_related('details_object')

    def get_queryset(self):
        return self.objects_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_widgets'] = self.filters
        return context

    def gather_filters(self):
        factory = FilterWidgetFactory()
        self.filters = []
        self.filters.append(
            factory('price',
                    FilterWidgetFactory.Filters.BOUND,
                    queryset=self.objects_list
                    )
        )
        self.filters.append(
            factory('manufacturer',
                    FilterWidgetFactory.Filters.DYNAMIC_CHOICES,
                    queryset=self.objects_list
                    )
        )

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
