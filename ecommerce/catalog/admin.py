from django.contrib import admin

from .models import Product, Category, PhoneDetails, FridgeDetails

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount_percent', 'units_available']
    # TODO: add button in Product admin leading to corresponding Details object.


admin.site.register(Category)
admin.site.register(PhoneDetails)
admin.site.register(FridgeDetails)
