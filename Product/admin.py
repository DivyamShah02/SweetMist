from django.contrib import admin
from .models import Product, Category

# Register your models here.
class AdminProduct(admin.ModelAdmin):
    list_display = ('title','slug','sku','category','price')
admin.site.register(Product,AdminProduct)

class AdminCategory(admin.ModelAdmin):
    list_display = ('category',)
admin.site.register(Category,AdminCategory)
