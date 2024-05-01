from django.contrib import admin
from .models import Cart,Order,OrderItem

# Register your models here.

class AdminCart(admin.ModelAdmin):
    list_display = ('user_id','session_id','product_id','qty','add_date')
admin.site.register(Cart,AdminCart)

class AdminOrder(admin.ModelAdmin):
    list_display = ('user_id', 'order_id', 'active', 'shipment', 'paid', 'order_date_time')
admin.site.register(Order,AdminOrder)

class AdminOrderItem(admin.ModelAdmin):
    list_display = ('order_id','product_id','qty','price')
admin.site.register(OrderItem,AdminOrderItem)