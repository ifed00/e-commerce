from django.shortcuts import render
from django.views.generic import ListView

from .models import Category

# Create your views here.


class IndexView(ListView):
    queryset = Category.objects.all()
    template_name = 'catalog/index_page.html'
    context_object_name = 'categories'
