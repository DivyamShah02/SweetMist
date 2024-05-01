from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, GenerateOTPViewSet, CheckOTPViewSet, LoginViewSet, LogoutViewSet, AccountView,  EditAccountData

register_router = DefaultRouter()
register_router.register(r'', RegisterViewSet, basename='register')
register_router.register(r'generate_otp', GenerateOTPViewSet, basename='generate_otp')
register_router.register(r'check_otp', CheckOTPViewSet, basename='check_otp')

login_router = DefaultRouter()
login_router.register(r'', LoginViewSet, basename='login')

account_router = DefaultRouter()
account_router.register(r'', AccountView, basename='account')
account_router.register(r'edit_account', EditAccountData, basename='edit_account')

logout_router = DefaultRouter()
logout_router.register(r'', LogoutViewSet, basename='logout')

urlpatterns =[
    path('register/',include(register_router.urls)),
    path('login/',include(login_router.urls)),
    path('account/',include(account_router.urls)),
    path('logout/',include(logout_router.urls)),
]

