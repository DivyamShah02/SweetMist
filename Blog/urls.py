from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import BlogView, BlogDetailView

blog_router = DefaultRouter()
blog_router.register(r'',BlogView,basename='blog')

blog_detail_router = DefaultRouter()
blog_detail_router.register(r'',BlogDetailView,basename='blog_detail')

urlpatterns =[
    path('blog/',include(blog_router.urls)),
    path('blog_detail/',include(blog_detail_router.urls)),
    
]

