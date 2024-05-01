from django.contrib import admin
from .models import Product

# Register your models here.
class AdminProduct(admin.ModelAdmin):
    list_display = ('title','slug','sku','category','price')
admin.site.register(Product,AdminProduct)
