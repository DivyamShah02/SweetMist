from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CartView, CheckOutView, PaymentView, OrderView, OrderDetailsView, InvoiceView, CheckPaymentView, CheckPaymentsView

cart_router = DefaultRouter()
cart_router.register(r'',CartView,basename='cart')
# router.register(r'add_product',AddProduct,basename='add_product')

check_out_router = DefaultRouter()
check_out_router.register(r'',CheckOutView,basename='check_out')
check_out_router.register(r'payment',PaymentView,basename='payment')

order_router = DefaultRouter()
order_router.register(r'',OrderView,basename='order')
order_router.register(r'check_payment',CheckPaymentView,basename='check_payment')
order_router.register(r'check_unpaid_payment',CheckPaymentsView,basename='check_unpaid_payment')

order_detail_router = DefaultRouter()
order_detail_router.register(r'', OrderDetailsView, basename='order_detail')
order_detail_router.register(r'invoice', InvoiceView, basename='invoice')

urlpatterns =[
    path('cart/',include(cart_router.urls)),
    path('check_out/',include(check_out_router.urls)),
    path('order/',include(order_router.urls)),
    path('order_detail/',include(order_detail_router.urls)),
    
]

