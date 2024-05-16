from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,redirect
from Product.models import Product
from UserProfile.models import UserData
from Order.models import Order, OrderItem
from datetime import datetime
from SweetMist.Utilities.email_sender import send_order_out_for_delivery_mail, send_order_delivered_mail



def report(request):
    user = request.user
    if request.user.is_authenticated and request.user.is_superuser:
        filter_date = datetime(2024, 5, 10, 11, 0, 0)
        all_type_order = []
        unpacked_order = []
        packed_order = []
        out_for_delivery_order = []
        delivered_order = []
        
        unpacked_order_data_db = Order.objects.filter(paid=True,order_date_time__gt = filter_date, made=False)
        unpacked_order_data_db = unpacked_order_data_db[::-1]
        all_type_order.append({'type':'unpacked_order_data_db','data':unpacked_order_data_db})
        
        packed_order_data_db = Order.objects.filter(paid=True, order_date_time__gt = filter_date, made=True, status='PL')
        packed_order_data_db = packed_order_data_db[::-1]
        all_type_order.append({'type':'packed_order_data_db','data':packed_order_data_db})
        
        out_for_deliver_order_data_db = Order.objects.filter(paid=True, order_date_time__gt = filter_date, made=True, status='IT')
        out_for_deliver_order_data_db = out_for_deliver_order_data_db[::-1]
        all_type_order.append({'type':'out_for_deliver_order_data_db','data':out_for_deliver_order_data_db})
        
        delivered_order_data_db = Order.objects.filter(paid=True, order_date_time__gt = filter_date, made=True, status='DV')
        delivered_order_data_db = delivered_order_data_db[::-1]
        all_type_order.append({'type':'delivered_order_data_db','data':delivered_order_data_db})

        for type_order in all_type_order:
            temp_order_data = []
            for order in type_order['data']:
                user_data = UserData.objects.filter(user_id=order.user_id).first()
                product_data = OrderItem.objects.filter(order_id=order.order_id)
                tot_amt = float(0)
                products = []
                for product in product_data:
                    tot_amt+=float(product.price)
                    product_data = Product.objects.filter(id=product.product_id).first()
                    products.append({'qty':product.qty, 'product_title':product_data.title, 'per_item':product.per_item_price})
                
                temp_data = {
                'order_id':order.order_id,
                'name' : f'{user_data.first_name} {user_data.last_name}',
                'tot_amt' : f'{tot_amt}',
                'number' : f'{user_data.number}',
                'items':products,
                'order_date' : f'{order.order_date_time}',
                'address' : f'{user_data.primary_address}, {user_data.secondary_address}, {user_data.city}, {user_data.state}, {user_data.country}, {user_data.pincode}.',
                }
                
                temp_order_data.append(temp_data)
            
            if type_order['type'] == 'unpacked_order_data_db':
                unpacked_order = temp_order_data
            
            elif type_order['type'] == 'packed_order_data_db':
                packed_order = temp_order_data
            
            elif type_order['type'] == 'out_for_deliver_order_data_db':
                out_for_deliver_order = temp_order_data
            
            elif type_order['type'] == 'delivered_order_data_db':
                delivered_order = temp_order_data

        data = {
            'unpacked_order':unpacked_order,
            'packed_order':packed_order,
            'out_for_deliver_order':out_for_deliver_order,
            'delivered_order':delivered_order,
        }


        return render(request, 'report_temp.html', data)
    else:
        return redirect('login-list')

def api_order_packed(request):
    try:
        if request.user.is_authenticated and request.user.is_superuser:
            order_id = request.GET.get('order_id')
            order_data_edit = Order.objects.get(order_id=order_id)
            order_data_edit.made = True
            order_data_edit.save()
            return JsonResponse({'success':True})
        
        else:
            return JsonResponse({'success':True,'details':'User is Authenticated'})
            
    except Exception as e:
        return JsonResponse({'success':False, 'details':str(e)})
    
def api_order_out_for_delivery(request):
    try:
        if request.user.is_authenticated and request.user.is_superuser:
            order_id = request.GET.get('order_id')
            order_data_edit = Order.objects.get(order_id=order_id)
            order_data_edit.status = 'IT'
            order_data_edit.in_transit_date = datetime.now()
            order_data_edit.save()
            try:
                user_data = UserData.objects.filter(user_id=order_data_edit.user_id).first()
                send_order_out_for_delivery_mail(order_id=order_id, to_email=user_data.email)
            except:
                pass
            
            return JsonResponse({'success':True})
        
        else:
            return JsonResponse({'success':True,'details':'User is Authenticated'})

    except Exception as e:
        return JsonResponse({'success':False, 'details':str(e)})
    
def api_order_delivered(request):
    try:
        if request.user.is_authenticated and request.user.is_superuser:
            order_id = request.GET.get('order_id')
            order_data_edit = Order.objects.get(order_id=order_id)
            order_data_edit.status = 'DV'
            order_data_edit.delivered = True
            order_data_edit.delivery_date = datetime.now()
            order_data_edit.save()
            user_data = UserData.objects.filter(user_id=order_data_edit.user_id).first()
            send_order_delivered_mail(order_id=order_id, to_email=user_data.email)
            return JsonResponse({'success':True})
        
        else:
            return JsonResponse({'success':True,'details':'User is Authenticated'})

    except Exception as e:
        return JsonResponse({'success':False, 'details':str(e)})


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
    if request.user.is_authenticated and request.user.is_superuser:
        order_edit = Order.objects.get(order_id='1624348960')
        order_edit.paid = False
        order_edit.pg_order_status = 'ACTIVE'
        order_edit.pg_payment_id = ''
        order_edit.save()
        return HttpResponse('Done')
    return JsonResponse({'success':False, 'Reason':'Unauthorized'})

def page_not_found(request, exception):
    return render(request, '404.html', status=404)
