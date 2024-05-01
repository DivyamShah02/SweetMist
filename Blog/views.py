from django.shortcuts import render, redirect
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from Product.models import Product
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from Logs.lg_logger import log_access, log_error, log_error_simple

class BlogView(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            return render(request, 'Blog/blog.html', status=status.HTTP_200_OK)
        
        except Exception as e:
            log_error(request, e)
            return redirect('home-list')  
    
class BlogDetailView(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            return render(request, 'Blog/blog-details.html', status=status.HTTP_200_OK)
        
        except Exception as e:
            log_error(request, e)
            return redirect('blog-list')  
