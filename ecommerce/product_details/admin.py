from django.contrib import admin

from .models import GarlandDetails, IlluminationDetails, WreathDetails, \
    DecorationDetails, GiftWrapDetails, FireworksDetails

from catalog.admin import DetailsAdmin

# Register your models here.

admin.site.register(GarlandDetails, DetailsAdmin)
admin.site.register(IlluminationDetails, DetailsAdmin)
admin.site.register(WreathDetails, DetailsAdmin)
admin.site.register(DecorationDetails, DetailsAdmin)
admin.site.register(GiftWrapDetails, DetailsAdmin)
admin.site.register(FireworksDetails, DetailsAdmin)
