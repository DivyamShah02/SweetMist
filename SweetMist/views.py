from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,redirect
from Product.models import Product

from Order.models import Order

def CustomGenerateSession(request):
    if request.user.is_authenticated:
        return JsonResponse({'success':True,'details':'User is Authenticated'})
    else:
        if request.session.get('session_token') is None:
            request.session['session_token'] = request.COOKIES.get('csrftoken')
        return JsonResponse({'success':True,'session_token':request.COOKIES.get('csrftoken')})


def api_check_sku(request):
    try:
        sku = request.GET.get('sku')
        if sku != '':
            same_sku = Product.objects.filter(sku=sku)
            if len(same_sku) > 0:
                return JsonResponse({'success': False})
            else:
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    except:
        return JsonResponse({'success': False})



def ProductAdderView(request):
    user = request.user
    if user.is_staff:
        pass
    else:
        return redirect('home')
    error = 0 # no error
    success = 0
    
    try:
        
        if request.method == 'POST':
            sku = request.POST.get('sku')
            same_sku = Product.objects.filter(sku=sku)
            
            title = request.POST.get('title')
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
            category = request.POST.get('category'),
            tags = request.POST.get('tags'),
            price = request.POST.get('price'),
            info = request.POST.get('info'),
            image_1 = request.FILES.get('image_1'),
            image_2 = request.FILES.get('image_2'),
            image_3 = request.FILES.get('image_3'),
            image_4 = request.FILES.get('image_4'),
            image_5 = request.FILES.get('image_5'),
            )
            new_product.save()
            success = 1
        
    except:
        error = 1
    
    data = {
        'error':error,
        'success':success,
    }
    return render(request,'Admin/product_adder.html',data)


def misc_temp(request):
    order_edit = Order.objects.get(order_id='1624348960')
    order_edit.paid = False
    order_edit.pg_order_status = 'ACTIVE'
    order_edit.pg_payment_id = ''
    order_edit.save()
    return HttpResponse('Done')
