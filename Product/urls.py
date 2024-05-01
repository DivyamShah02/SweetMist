from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import Shop, ShopDetails, AddProduct, CheckSku


product_router = DefaultRouter()
product_router.register(r'',Shop,basename='shop')
product_router.register(r'prod_details',ShopDetails,basename='prod_details')

admin_product_router = DefaultRouter()
admin_product_router.register(r'add_product',AddProduct,basename='add_product')
admin_product_router.register(r'check_sku',CheckSku,basename='check_sku')

urlpatterns =[
    path('shop/',include(product_router.urls)),
    
    path('admin_prod/',include(admin_product_router.urls)),
]

