from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Product, Category, PhoneDetails, FridgeDetails

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount_percent', 'units_available']
    readonly_fields = ['url_to_details']

    @admin.decorators.display(description='URL to details entry')
    def url_to_details(self, product: Product):
        meta = product.details_object._meta  # Django documentation implies _meta is public member
        if product.details_id is not None:
            url = reverse(f'admin:{meta.app_label}_{meta.model_name}_change', args=[product.details_id])
            text = f'{meta.model_name}(id={product.details_id})'
        else:
            url = reverse(f'admin:{meta.app_label}_{meta.model_name}_add')
            text = f'Add new {meta.model_name}'

        return mark_safe(f'<a href={url}>{text}</a>')


admin.site.register(Category)
admin.site.register(PhoneDetails)
admin.site.register(FridgeDetails)
