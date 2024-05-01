from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import HomeView, ContactView, FaqView

home_router = DefaultRouter()
home_router.register(r'',HomeView,basename='home')

contact_router = DefaultRouter()
contact_router.register(r'',ContactView,basename='contact')

faq_router = DefaultRouter()
faq_router.register(r'',FaqView,basename='faq')

urlpatterns =[
    path('',include(home_router.urls)),
    path('contact/',include(contact_router.urls)),
    path('Faq/',include(faq_router.urls)),
    
]

