from django.urls import path

from .views import IndexView, CategoryView, ProductView, SearchView, OrderView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('category/<slug:slug>', CategoryView.as_view(), name='category'),
    path('product/<slug:cat_slug>/<int:id>', ProductView.as_view(), name='product'),
    path('search', SearchView.as_view(), name='search'),

    path('order/<uuid:order_id>', OrderView.as_view(), name='order')
]
