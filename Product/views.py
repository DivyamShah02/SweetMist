from django.shortcuts import render,redirect
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category
from rest_framework.permissions import AllowAny
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from Logs.lg_logger import log_access, log_error, log_error_simple


class Shop(ViewSet):
    '''Shop API **All products detials'''
    # permission_classes = [IsAuthenticated]
    def list(self, request):
        log_access(request)
        try:
            category = request.query_params.get('category')
            print(category)
            print('sghrtshtshtht')
            if category:
                all_prods = Product.objects.filter(category=category)
                if len(all_prods) == 0:
                    all_prods = Product.objects.all()
            else:
                all_prods = Product.objects.all()

            serializer = ProductSerializer(all_prods,many=True)
            categories = Category.objects.all()
            
            data = {
                'products':serializer.data,
                'categories':categories,
                'category':category,
            }
            
            return render(request, 'Product/shop.html', data, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_error(request, e)
            return redirect('home-list')  


class ShopDetails(ViewSet):
    '''Perticular product details'''
    # permission_classes = [IsAuthenticated]
    def list(self, request):
        log_access(request)
        try:
            slug = request.query_params.get('slug')
            prod_details = Product.objects.filter(slug=slug).first()
            if prod_details:
                serializer = ProductSerializer(prod_details)
                data = {
                    'product_data':serializer.data
                }
                return render(request, 'Product/product.html', data, status=status.HTTP_200_OK)
                # return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                return redirect('shop-list')
                # return Response({'details':'Product does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            log_error(request, e)
            return redirect('shop-list')  



### Admin Class for adding new product
class AddProduct(ViewSet):
    '''Create a new product'''
    permission_classes = [IsAuthenticated]
    def create(self, request):
        log_access(request)
        try:
            if request.user.is_staff:
                sku = request.data.get('sku')
                title = request.data.get('title')
                slug = str(title).replace(' ','-')
                not_unique_slug = True
                index = 0
                
                while not_unique_slug:
                    index += 1
                    same_slug = Product.objects.filter(slug=slug)
                    if len(same_slug) > 0:
                        slug = slug.replace(f'-({index - 1})','') + f'-({index})'
                    else:
                        not_unique_slug = False
                        
                new_product = Product(
                title = title,
                slug = slug,
                sku = sku,
                category = request.data.get('category'),
                tags = request.data.get('tags'),
                price = request.data.get('price'),
                info = request.data.get('info'),
                image_1 = request.FILES.get('image_1'),
                image_2 = request.FILES.get('image_2'),
                image_3 = request.FILES.get('image_3'),
                image_4 = request.FILES.get('image_4'),
                image_5 = request.FILES.get('image_5'),
                )
                new_product.save()
                serializer = ProductSerializer(new_product)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            else:
                return Response({'details':'Admin auth failed.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            log_error(request, e)
            return Response({'details':{e}}, status=status.HTTP_400_BAD_REQUEST)


class CheckSku(ViewSet):
    '''API to check SKU'''
    permission_classes = [IsAuthenticated]
    def list(self, request):
        log_access(request)
        try:
            if request.user.is_staff:
                sku = request.query_params.get('sku')
                if sku != '':
                    same_sku = Product.objects.filter(sku=sku)
                    if len(same_sku) > 0:
                        return Response({'success': False},status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({'success': True},status=status.HTTP_200_OK)
                else:
                    return Response({'success': False},status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({'details':'Admin auth failed.'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            log_error(request, e)
            return Response({'success': False, 'details':e},status=status.HTTP_404_NOT_FOUND)

