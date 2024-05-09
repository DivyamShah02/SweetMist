from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from .views import CustomGenerateSession, ProductAdderView, api_check_sku, misc_temp, page_not_found
from django.views.generic import RedirectView

urlpatterns = [
    path('misc_temp/', misc_temp, name='misc_temp'),
    path('admin/', admin.site.urls),
    path('admin_product_adder/',ProductAdderView, name='admin_product_adder'),
    path('api_check_sku/',api_check_sku,name='api_check_sku'),
    
    
    path('generate_session/',CustomGenerateSession,name='generate_session'),
    
    path('favicon.ico', RedirectView.as_view(url='/static/SweetMist.png')),
    
    
    path('',include('Product.urls')),
    path('',include('Order.urls')),
    path('',include('UserProfile.urls')),
    path('',include('MainPages.urls')),
    path('',include('Blog.urls')),
    
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = page_not_found

