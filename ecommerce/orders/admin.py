from django.contrib import admin

from .models import Order, OrderProducts

# Register your models here.


class OrderProductsInline(admin.TabularInline):
    model = OrderProducts


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    inlines = [OrderProductsInline]


@admin.register(OrderProducts)
class OrderProductsAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id']
    list_display_links = ['id', 'order_id']
