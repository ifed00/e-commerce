from django.urls import path

from .views import OrderView

urlpatterns = [
    path('<uuid:order_id>', OrderView.as_view(), name='order')
]
