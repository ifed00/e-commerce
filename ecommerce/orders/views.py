from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.models import AnonymousUser

from .models import Order, OrderProducts


# Create your views here.


class OrderView(ListView):
    template_name = 'orders/order.html'
    context_object_name = 'product_details'

    def get_queryset(self):
        order = get_object_or_404(Order, pk=self.kwargs['order_id'])

        self.order = order

        if (isinstance(self.request.user, AnonymousUser) or
                self.order.user.id != self.request.user.id):
            raise PermissionDenied

        return OrderProducts.objects.filter(order=order).select_related('product')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(objects_list=object_list, **kwargs)

        context['order'] = self.order

        return context
