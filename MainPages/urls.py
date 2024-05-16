from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import HomeView, ContactView, FaqView, PrivacyView, TermsCondsView

home_router = DefaultRouter()
home_router.register(r'',HomeView,basename='home')

contact_router = DefaultRouter()
contact_router.register(r'',ContactView,basename='contact')

faq_router = DefaultRouter()
faq_router.register(r'',FaqView,basename='faq')

privacy_router = DefaultRouter()
privacy_router.register(r'',PrivacyView,basename='privacy')

terms_conds_router = DefaultRouter()
terms_conds_router.register(r'',TermsCondsView,basename='terms_conds')

urlpatterns =[
    path('',include(home_router.urls)),
    path('contact/',include(contact_router.urls)),
    path('Faq/',include(faq_router.urls)),
    path('privacy_policy/',include(privacy_router.urls)),
    path('terms_conditions/',include(terms_conds_router.urls)),
    
]

