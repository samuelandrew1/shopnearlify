from django.contrib import admin
from .models import *


# Register your models here.
class AbujaLocationAdmin(admin.ModelAdmin):
    list_display = ("state",)
    search_fields = ("state",)


admin.site.register(DeliveryLocations, AbujaLocationAdmin)
