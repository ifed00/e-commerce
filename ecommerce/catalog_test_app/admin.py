from django.contrib import admin

from .models import PhoneDetails, FridgeDetails

from catalog.admin import DetailsAdmin

# Register your models here.

admin.site.register(PhoneDetails, DetailsAdmin)
admin.site.register(FridgeDetails, DetailsAdmin)
