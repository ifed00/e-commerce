from django.urls import path

from .views import IndexView, CategoryView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('category/<slug:slug>', CategoryView.as_view(), name='category')
]
