from django.urls import path

from .views import IndexView, CategoryView, ProductView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('category/<slug:slug>', CategoryView.as_view(), name='category'),
    path('product/<slug:cat_slug>/<int:id>', ProductView.as_view(), name='product')
]
