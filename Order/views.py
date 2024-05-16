from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, Order, OrderItem
from UserProfile.models import UserData
from Product.models import Product
from rest_framework.permissions import AllowAny
from .serializers import CartSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated
import random
from Logs.lg_logger import log_access, log_error, log_error_simple
from SweetMist.Utilities.payment import create_pg_order, check_payment, get_payment_details
from SweetMist.Utilities.email_sender import send_order_success_mail
import json


class CartView(ViewSet):
    # permission_classes = [IsAuthenticated]
    def list(self, request):
        log_access(request)
        if request.user.is_authenticated:
            items = Cart.objects.filter(user_id=request.user,active=True)
        else:
            # session_id = request.query_params.get('session_token')
            session_id = request.session.get('session_token') # Storing csrftoken instead of session id
            items = Cart.objects.filter(session_id=session_id,active=True)
        all_items = []
        cart_total = float(0)

        for item in items:
            item_data = Product.objects.filter(id=item.product_id).first()
            if item.active:
                total_price = float(item_data.price) * float(item.qty)
                cart_total += total_price
                all_items.append({
                    'id':item.id,
                    'product_id':item.product_id,
                    'title':item_data.title,
                    'slug':item_data.slug,
                    'sku':item_data.sku,
                    'category':item_data.category,
                    'tags':item_data.tags,
                    'price':item_data.price,
                    'total_price':total_price,
                    'image_1':item_data.image_1.url,
                    'cart_image':item_data.cart_image.url,
                    'qty':item.qty,
                    'add_date':item.add_date,
                    'active':item.active,
                })
        
        if len(all_items) == 0:
            empty_cart = True
        
        else:
            empty_cart = False
        
        data = {
            'success': True,
            'items': all_items,
            'empty_cart':empty_cart,
            'len_of_item': len(all_items),
            'cart_total': round(cart_total, 2),
            'status': status.HTTP_200_OK,
        }

        if request.query_params.get('is_api') == 'True':
            return JsonResponse(data=data, status=status.HTTP_200_OK)

        return render(request, 'Order/shopping-cart.html', data, status=status.HTTP_200_OK)

    def create(self, request):
        log_access(request)
        try:
            slug = request.query_params.get('slug')
            product_info = Product.objects.filter(slug=slug).first()
            if product_info:
                qty = request.query_params.get('qty')
                if request.user.is_authenticated:
                    session_id = request.session.get('session_token')
                    item_already_in_cart = Cart.objects.filter(user_id=request.user, product_id=product_info.id, active=True).first()
                    if item_already_in_cart:
                        print('here')
                        item_edit_in_cart = Cart.objects.get(user_id=request.user, product_id=product_info.id, active=True)
                        print(item_edit_in_cart)
                        item_edit_in_cart.qty = int(item_edit_in_cart.qty) + int(qty)
                        item_edit_in_cart.save()
                    
                    else:
                        new_item = Cart(user_id=request.user, session_id=session_id, product_id=product_info.id, qty=qty)
                        new_item.save()

                else:
                    # session_id = request.session.session_key
                    session_id = request.session.get('session_token') # Storing csrftoken (stored as session_token) instead of session id
                    new_item = Cart(session_id=session_id, product_id=product_info.id, qty=qty)
                    new_item.save()

                return Response({'success': True},status=status.HTTP_200_OK)
            
            return Response({'success': False,'details':'Product does not exist.'},status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            log_error(request, e)
            return Response({'success': False,'details':e},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            item_id = request.query_params.get('item_id')
            item = Cart.objects.get(id=item_id)
            if item:
                qty = request.query_params.get('qty')

                item.qty = qty
                item.save()

                serializer = CartSerializer(item)
                return Response({'success': True, 'item': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'details': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'success': False, 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        item_id = request.query_params.get('item_id')
        item_details = Cart.objects.filter(id=item_id).first()

        if item_details:
            item_details.delete()
            return Response({'success':True, 'detail': 'Item deleted successfully.'}, status=status.HTTP_200_OK)

        return Response({'success':False, 'detail': 'Item does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class CheckOutView(ViewSet):
    def list(self, request):
        log_access(request)
        if request.query_params.get('cart_checkout') == 'True':
            user_logged_in = False
            user_data = None
            if request.user.is_authenticated:
                items = Cart.objects.filter(user_id=request.user,active=True)
                user_logged_in = True
                user_data = UserData.objects.filter(user_id=request.user).first()
            else:
                # session_id = request.query_params.get('session_token')
                session_id = request.session.get('session_token') # Storing csrftoken instead of session id
                items = Cart.objects.filter(session_id=session_id,active=True)
            all_items = []
            cart_total = float(0)

            for item in items:
                item_data = Product.objects.filter(id=item.product_id).first()
                if item.active:
                    total_price = float(item_data.price) * float(item.qty)
                    cart_total += total_price
                    all_items.append({
                        'id':item.id,
                        'title':item_data.title,
                        'slug':item_data.slug,
                        'sku':item_data.sku,
                        'category':item_data.category,
                        'tags':item_data.tags,
                        'price':item_data.price,
                        'total_price':total_price,
                        'image_1':item_data.image_1.url,
                        'qty':item.qty,
                        'add_date':item.add_date,
                        'active':item.active,
                    })
            
            data = {
                'success': True,
                'items': all_items,
                'len_of_item': len(all_items),
                'cart_total': round(cart_total, 2),
                'user_logged_in':user_logged_in,
                'user_data':user_data,
                'cart_checkout':True,
                'status': status.HTTP_200_OK,
            }

            if request.query_params.get('is_api') == 'True':
                return JsonResponse(data=data, status=status.HTTP_200_OK)

            return render(request, 'Order/check-out.html', data, status=status.HTTP_200_OK)

        elif request.query_params.get('product_id'):
            user_logged_in = False
            user_data = None
            if request.user.is_authenticated:
                user_logged_in = True
                user_data = UserData.objects.filter(user_id=request.user).first()
            
            product_id = request.query_params.get('product_id')
            qty = request.query_params.get('qty')
            all_items = []
            item_data = Product.objects.filter(id=product_id).first()
            total_price = float(item_data.price) * float(qty)
            all_items.append({
                'id':product_id,
                'title':item_data.title,
                'slug':item_data.slug,
                'sku':item_data.sku,
                'category':item_data.category,
                'tags':item_data.tags,
                'price':item_data.price,
                'total_price':total_price,
                'image_1':item_data.image_1.url,
                'qty':qty,
            })
            
            data = {
                'success': True,
                'items': all_items,
                'len_of_item': len(all_items),
                'cart_total': round(total_price, 2),
                'user_data':user_data,
                'user_logged_in':user_logged_in,
                'cart_checkout':False,
                'qty':qty,
                'product_id':product_id,
                'status': status.HTTP_200_OK,
            }


            return render(request, 'Order/check-out.html', data, status=status.HTTP_200_OK)

        else:
            return redirect('cart-list')

class PaymentView(ViewSet):
    def list(self, request):
        log_access(request)
        if request.query_params.get('cart_checkout') == 'True':
            user_logged_in = False
            user_data = None
            if request.user.is_authenticated:
                items = Cart.objects.filter(user_id=request.user,active=True)
                user_logged_in = True
                user_data = UserData.objects.filter(user_id=request.user).first()
            else:
                # session_id = request.query_params.get('session_token')
                session_id = request.session.get('session_token') # Storing csrftoken instead of session id
                items = Cart.objects.filter(session_id=session_id,active=True)
            all_items = []
            cart_total = float(0)

            for item in items:
                item_data = Product.objects.filter(id=item.product_id).first()
                if item.active:
                    total_price = float(item_data.price) * float(item.qty)
                    cart_total += total_price
                    all_items.append({
                        'id':item.id,
                        'title':item_data.title,
                        'slug':item_data.slug,
                        'sku':item_data.sku,
                        'category':item_data.category,
                        'tags':item_data.tags,
                        'price':item_data.price,
                        'total_price':total_price,
                        'image_1':item_data.image_1.url,
                        'qty':item.qty,
                        'add_date':item.add_date,
                        'active':item.active,
                    })
            
            data = {
                'success': True,
                'items': all_items,
                'len_of_item': len(all_items),
                'cart_total': round(cart_total, 2),
                'user_logged_in':user_logged_in,
                'user_data':user_data,
                'cart_checkout':True,
                'status': status.HTTP_200_OK,
            }

            if request.query_params.get('is_api') == 'True':
                return JsonResponse(data=data, status=status.HTTP_200_OK)

            return render(request, 'Order/payment.html', data, status=status.HTTP_200_OK)

        elif request.query_params.get('product_id'):
            user_logged_in = False
            user_data = None
            if request.user.is_authenticated:
                user_logged_in = True
                user_data = UserData.objects.filter(user_id=request.user).first()
            
            product_id = request.query_params.get('product_id')
            qty = request.query_params.get('qty')
            all_items = []
            item_data = Product.objects.filter(id=product_id).first()
            total_price = float(item_data.price) * float(qty)
            all_items.append({
                'id':product_id,
                'title':item_data.title,
                'slug':item_data.slug,
                'sku':item_data.sku,
                'category':item_data.category,
                'tags':item_data.tags,
                'price':item_data.price,
                'total_price':total_price,
                'image_1':item_data.image_1.url,
                'qty':qty,
            })
            
            data = {
                'success': True,
                'items': all_items,
                'len_of_item': len(all_items),
                'cart_total': round(total_price, 2),
                'user_data':user_data,
                'user_logged_in':user_logged_in,
                'cart_checkout':False,
                'qty':qty,
                'product_id':product_id,
                'status': status.HTTP_200_OK,
            }


            return render(request, 'Order/payment.html', data, status=status.HTTP_200_OK)

        else:
            return redirect('cart-list')

class OrderView(ViewSet):
    def create(self,request):
        log_access(request)
        try:
            if request.data.get('cart_checkout') == 'True':
                new_id = True
                
                while new_id:
                    oid = random.randint(1111111111, 9999999999)
                    if len(Order.objects.filter(order_id=oid)) == 0:
                        new_id = False

                new_order = Order(user_id=request.user, order_id=oid, shipment=False)
                new_order.save()
                
                items = Cart.objects.filter(user_id=request.user,active=True)
                
                final_total_price = 0

                for item in items:
                    item_data = Product.objects.filter(id=item.product_id).first()

                    if item.active:
                        # Removing the item form cart
                        item_obj = Cart.objects.get(id=item.id)
                        item_obj.active = False
                        item_obj.save()
                        
                        total_price = float(item_data.price) * float(item.qty)
                        final_total_price += total_price
                        new_order_item = OrderItem(order_id=oid, product_id=item.product_id, qty=item.qty, price=total_price, per_item_price=item_data.price)
                        new_order_item.save()
            
            else:
                # Creating new order
                product_id = request.data.get('product_id')
                qty = request.data.get('qty')
                product_data = Product.objects.filter(id=product_id).first()
                final_total_price = 0
                total_price = float(product_data.price) * float(qty)
                final_total_price += total_price
                
                new_id = True
                
                while new_id:
                    oid = random.randint(1111111111, 9999999999)
                    if len(Order.objects.filter(order_id=oid)) == 0:
                        new_id = False

                new_order = Order(user_id=request.user, order_id=oid, shipment=False)
                new_order.save()

                new_order_item = OrderItem(order_id=oid, product_id=product_id, qty=qty, price=total_price, per_item_price=product_data.price)
                new_order_item.save()

            user_data = UserData.objects.filter(user_id=request.user).first()

            pg_order_created, pg_order_data = create_pg_order(
                order_id=f'{oid}', 
                order_amount=final_total_price, 
                customer_email=user_data.email, 
                customer_name=f'{user_data.first_name} {user_data.last_name}', 
                customer_id=f'{user_data.user_id}', 
                customer_phone=f'{str(user_data.number).replace("+91 ", "")}')

            if pg_order_created is True:
                order_edit = Order.objects.get(order_id=oid)
                order_edit.payment_session_id = pg_order_data['payment_session_id']
                order_edit.pg_order_id = pg_order_data['cf_order_id']
                order_edit.pg_order_status = pg_order_data['order_status']
                order_edit.active = True
                order_edit.save()

                return Response({'success':True, 'oid':oid, 'pg_data':pg_order_data, 'pg_session_id':pg_order_data['payment_session_id']})

            else:
                return Response({'success':False,'details':f'Error while generating pg order : {pg_order_data}'})
            
            return redirect(f"/order_detail/?order_id={oid}&order_placed=True")
            # return render(request, 'Order/order_confirm.html', status=status.HTTP_200_OK)

        except Exception as e:
            log_error(request, e)
            return Response({'success':False,'details':e})


class CheckPaymentView(ViewSet):
    def create(self, request):
        log_access(request)
        try:
            payment_session_id = request.data.get('payment_session_id')
            oid = request.data.get('oid')
            order_data = Order.objects.filter(order_id=oid, payment_session_id=payment_session_id).first()

            if order_data:
                pg_payment, pg_payment_data = get_payment_details(order_id=f'{oid}')
                if pg_payment:
                    if pg_payment_data['is_captured']:
                        order_edit = Order.objects.get(order_id=oid, payment_session_id=payment_session_id)
                        order_edit.paid = True
                        order_edit.pg_order_status = pg_payment_data['payment_status']
                        order_edit.pg_payment_id = pg_payment_data['cf_payment_id']
                        order_edit.status = 'PL'
                        order_edit.email_sent = send_order_success_mail(order_id=f'{oid}', to_email=request.user.email)
                        order_edit.save()

                        return Response({'success':True, 'paid':True, 'oid':oid})

                    else:
                        return Response({'success':False, 'paid':False, 'details':'Payment still not received'})
                
                else:
                    return Response({'success':False, 'paid':False, 'details':f'Error in checking payment status'})
            
            else:
                return Response({'success':False, 'paid':False, 'details':'Order details not found'})

        except Exception as e:
            log_error(request, e)
            return Response({'success':False, 'paid':False, 'details':e})


class OrderDetailsView(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            if request.user.is_authenticated:
                user_data = UserData.objects.filter(user_id=request.user).first()
                order_id = request.query_params.get('order_id')
                order_placed = request.query_params.get('order_placed')
                order_data = Order.objects.filter(user_id=request.user, order_id=order_id).first()
                if order_data:
                    if order_data.active:
                        order_date = order_data.order_date_time.strftime("%d %b, %Y")
                        all_order_items = OrderItem.objects.filter(order_id=order_id)
                        all_items = []
                        order_total = float(0)

                        for item in all_order_items:
                            item_data = Product.objects.filter(id=item.product_id).first()
                            total_price = float(item_data.price) * float(item.qty)
                            order_total += total_price
                            all_items.append({
                                'id':item.id,
                                'product_id':item.product_id,
                                'title':item_data.title,
                                'slug':item_data.slug,
                                'sku':item_data.sku,
                                'category':item_data.category,
                                'tags':item_data.tags,
                                'price':item.per_item_price,
                                'total_price':total_price,
                                'image_1':item_data.image_1.url,
                                'qty':item.qty,
                            })

                        if not order_data.paid:
                            got_payment_details, payment_details = get_payment_details(order_id=order_id)

                            if got_payment_details:
                                if payment_details['is_captured']:
                                    order_edit = Order.objects.get(order_id=order_id)
                                    order_edit.paid = True
                                    order_edit.pg_order_status = payment_details['payment_status']
                                    order_edit.pg_payment_id = payment_details['cf_payment_id']
                                    order_edit.status = 'PL'                    
                                    order_edit.save()
                                    if not order_data.email_sent:
                                        order_edit = Order.objects.get(order_id=order_id)
                                        order_edit.email_sent = send_order_success_mail(order_id=order_id, to_email=request.user.email)
                                        order_edit.save()      

                            else:
                                payment_details = None

                            
                        else:
                            got_payment_details = False
                            payment_details = None
                        
                      
                        
                        
                        order_data = Order.objects.filter(user_id=request.user, order_id=order_id).first()
                        status_codes = {
                            'UP': 'Unpaid',
                            'PL': 'Order Placed',
                            'IT': 'In Transit',
                            'DV': 'Delivered',
                        }
                        order_status = status_codes[order_data.status]
                        order_status_text = []
                        
                        if order_status == 'Order Placed':
                            head = f'Order was successfully placed (Order ID: #{order_id})'
                            body = f'{order_date}'
                            foot = f'Your order has been placed successfully'
                            order_status_text.append({'head':head, 'body':body, 'foot':foot})
                        
                        if order_status == 'In Transit':
                            head = f'Order was successfully placed (Order ID: #{order_id})'
                            body = f'{order_date}'
                            foot = f'Your order has been placed successfully'
                            order_status_text.append({'head':head, 'body':body, 'foot':foot})
                            
                            in_transit_date = order_data.in_transit_date.strftime("%d %b, %Y")
                            head = f'Order out for delivery'
                            body = f'{in_transit_date}'
                            foot = f'Your order has been handed to delivery partner and will be delivered shortly'
                            order_status_text.append({'head':head, 'body':body, 'foot':foot})
                            
                        if order_status == 'Delivered':
                            head = f'Order was successfully placed (Order ID: #{order_id})'
                            body = f'{order_date}'
                            foot = f'Your order has been placed successfully'
                            order_status_text.append({'head':head, 'body':body, 'foot':foot})
                            
                            in_transit_date = order_data.in_transit_date.strftime("%d %b, %Y")
                            head = f'Order out for delivery'
                            body = f'{in_transit_date}'
                            foot = f'Your order has been handed to delivery partner and will be delivered shortly'
                            order_status_text.append({'head':head, 'body':body, 'foot':foot})
                            
                            delivery_date = order_data.delivery_date.strftime("%d %b, %Y")
                            head = f'Order delivered'
                            body = f'{delivery_date}'
                            foot = f'Your order has been successfully delivered'
                            order_status_text.append({'head':head, 'body':body, 'foot':foot})
                        

                        data = {
                            'success': True,
                            'order_data':order_data,
                            'order_status':order_status,
                            'order_status_text':order_status_text,
                            'user_data':user_data,
                            'order_date':order_date,
                            'order_id':order_id,
                            'items': all_items,
                            'len_of_item': len(all_items),
                            'order_total': round(order_total, 2),
                            'status': status.HTTP_200_OK,
                            'order_placed':bool(order_placed),
                            'got_payment_details':got_payment_details,
                            'payment_details': payment_details,
                        }

                        return render(request, 'Order/order_detail.html', data)

                    else:
                        return redirect('account-list')

                else:
                    return redirect('account-list')
            else:
                return redirect('account-list')
        
        except Exception as e:
            log_error(request, e)
            return redirect('account-list')    


class InvoiceView(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            if request.user.is_authenticated:
                user_data = UserData.objects.filter(user_id=request.user).first()
                order_id = request.query_params.get('order_id')
                order_data = Order.objects.filter(user_id=request.user, order_id=order_id).first()
                if order_data:
                    order_date = order_data.order_date_time.strftime("%d %b, %Y")                    
                    all_order_items = OrderItem.objects.filter(order_id=order_id)
                    all_items = []
                    order_total = float(0)

                    for item in all_order_items:
                        item_data = Product.objects.filter(id=item.product_id).first()
                        total_price = float(item_data.price) * float(item.qty)
                        order_total += total_price
                        all_items.append({
                            'id':item.id,
                            'product_id':item.product_id,
                            'title':item_data.title,
                            'slug':item_data.slug,
                            'sku':item_data.sku,
                            'category':item_data.category,
                            'tags':item_data.tags,
                            'price':item.per_item_price,
                            'total_price':total_price,
                            'image_1':item_data.image_1.url,
                            'qty':item.qty,
                        })

                    data = {
                        'success': True,
                        'user_data':user_data,
                        'order_date':order_date,                        
                        'order_id':order_id,
                        'items': all_items,
                        'len_of_item': len(all_items),
                        'order_total': round(order_total, 2),
                        'status': status.HTTP_200_OK,
                    }
                    return render(request, 'Order/invoice.html', data)
                else:
                    return redirect('account-list')
            else:
                return redirect('account-list')
        
        except Exception as e:
            log_error(request, e)
            return redirect('account-list')

class CheckPaymentsView(ViewSet):
    def list(self,request):
        log_access(request)
        try:
            all_unpaid_orders = Order.objects.filter(paid=False)
            for order_data in all_unpaid_orders:
                got_payment_details, payment_details = get_payment_details(order_id=order_data.order_id)
                if got_payment_details:
                    if payment_details['is_captured']:
                        order_edit = Order.objects.get(order_id=order_data.order_id)
                        order_edit.paid = True
                        order_edit.pg_order_status = payment_details['payment_status']
                        order_edit.pg_payment_id = payment_details['cf_payment_id']
                        order_edit.status = 'PL'                        
                        order_edit.save()
                        if not order_data.email_sent:
                            order_edit = Order.objects.get(order_id=order_data.order_id)
                            user = UserData.objects.filter(user_id=order_data.user_id).first()
                            order_edit.email_sent = send_order_success_mail(order_id=order_data.order_id, to_email=user.email)
                            order_edit.save()
            return JsonResponse({'success':True})

        except Exception as e:
            log_error(request, e)
            return JsonResponse({'success':False, 'details':e})
