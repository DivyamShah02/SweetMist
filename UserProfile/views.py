from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from Logs.lg_logger import log_access, log_error, log_error_simple
from SweetMist.Utilities.email_sender import send_otp_mail

from Product.models import Product
from .serializers import UserDataSerializer, OtpSerializer
from .models import UserData, Otp
from Order.models import Cart, Order, OrderItem

import json
import random
import secrets


class RegisterViewSet(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            return render(request, 'UserProfile/register.html', status=status.HTTP_200_OK)

        except Exception as e:
            log_error(request, e)
            return redirect('home-list')
    
    def create(self, request):
        log_access(request)
        try:
            session_token = request.session.get('session_token')

            # first_name = request.query_params.get('first_name')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            number = request.data.get('number')
            number = f'+91 {number}'
            email = request.data.get('email')
            password = request.data.get('password')
            otp_token = request.data.get('otp_token')
            primary_address = request.data.get('primary_address')
            secondary_address = request.data.get('secondary_address')
            city = request.data.get('city')
            state = request.data.get('state')
            country = request.data.get('country')
            pincode = request.data.get('pincode')
            from_checkout = request.data.get('from_checkout')

            if not Otp.objects.filter(token=otp_token, active=False, number=number).first():
                return Response({'success': False, 'reason':'OTP is not verified.', 'otp_not_verified':True, 'email_already_exists':False}, status=status.HTTP_400_BAD_REQUEST)

            if UserData.objects.filter(email=email).first():
                return Response({'success': False, 'reason':'Email Id already exists.', 'otp_not_verified':False, 'email_already_exists':True}, status=status.HTTP_400_BAD_REQUEST)

            new_id = True
            while new_id:
                uid = random.randint(1111111111, 9999999999)
                if len(User.objects.filter(username=uid)) == 0:
                    new_id = False

            user = User.objects.create_user(username=uid, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            if from_checkout:
                new_user = UserData(user_id=uid, email=email, password=password, number=number, first_name=first_name, last_name=last_name, primary_address=primary_address, secondary_address=secondary_address, city=city, state=state, country=country, pincode=pincode)
            else:
                new_user = UserData(user_id=uid, email=email, password=password, number=number, first_name=first_name, last_name=last_name)
            new_user.save()

            fun_cart_sync(request=request, user_id=uid)
            user = authenticate(request, username=uid, password=password)
            login(request, user)
            request.session.set_expiry(30 * 24 * 60 * 60)
            # return redirect('account-list')

            return Response({'success': True}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            log_error(request, e)
            return Response({'success': False, 'reason':f'{e}', 'otp_not_verified':False, 'email_already_exists':False}, status=status.HTTP_400_BAD_REQUEST)

class GenerateOTPViewSet(ViewSet):
    def create(self, request):
        log_access(request)
        try:
            session_token = request.session.get('session_token')
            number = request.data.get('number')
            module = request.data.get('module')
            number = f'+91 {number}'
            email = request.data.get('email')
            
            user_exist = UserData.objects.filter(number=number).first()
            
            if user_exist and module == 'register':
                return Response({'success': False, 'reason':'User alreaady exist.', 'error_occured':False, 'already_exist': True}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user_exist and module == 'reset_password':
                return Response({'success': False, 'reason':'User doesnot exist.', 'error_occured':False, 'does_not_exist': True}, status=status.HTTP_400_BAD_REQUEST)            

            gen_otp = random.randint(111111, 999999)
            token = secrets.token_hex(15)
            new_otp = Otp(session_id=session_token, otp=str(gen_otp), token=token, number=number, attempts=1)
            new_otp.save()
            print(gen_otp)
            # send_otp_mail(otp=gen_otp, to_email=email)

            
            # return Response({'success': True, 'otp_token': token}, status=status.HTTP_201_CREATED)
            return Response({'success': True, 'otp_token': token, 'otp':gen_otp}, status=status.HTTP_201_CREATED)
        except Exception as e:
            log_error(request, e)
            return Response({'success': False, 'reason':f'{e}', 'error_occured':True, 'already_exist': False}, status=status.HTTP_400_BAD_REQUEST)

class CheckOTPViewSet(ViewSet):
    def create(self, request):
        log_access(request)
        try:
            session_token = request.session.get('session_token')
            user_otp = request.data.get('otp')
            user_number = request.data.get('number')
            user_number = f'+91 {user_number}'
            otp_token = request.data.get('otp_token')
            attempts = 0
            otp_from_db = Otp.objects.filter(session_id=session_token, token=otp_token, number=user_number).first()

            if otp_from_db:
                real_otp = otp_from_db.otp
                attempts = int(otp_from_db.attempts)
                if attempts <= 2:
                    otp_obj = Otp.objects.get(id=otp_from_db.id)
                    if user_otp == real_otp:
                        otp_obj.active = False
                        otp_obj.attempts = attempts + 1
                        otp_obj.save()
                    
                        return Response({'success': True, 'generate_otp': False, 'attempts': attempts})
                    
                    else:
                        otp_obj.attempts = attempts + 1
                        otp_obj.save()
                        return Response({'success': False, 'reason':'Wrong OTP.', 'wrong_otp':True, 'generate_otp': False, 'attempts': attempts})

                else:
                    return Response({'success': False, 'reason':'No more attempts left.', 'wrong_otp':False, 'attempts_exceeded':True, 'generate_otp': False, 'attempts': attempts})
                    
            else:
                return Response({'success': False, 'reason':'No otp found.', 'wrong_otp':False, 'attempts_exceeded':False,  'generate_otp': True, 'attempts': attempts})

        except Exception as e:
            log_error(request, e)
            return Response({'success': False, 'reason':f'{e}', 'wrong_otp':False, 'attempts_exceeded':False,  'generate_otp': True, 'attempts': attempts})


class LoginViewSet(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            return render(request, 'UserProfile/login.html', status=status.HTTP_200_OK)

        except Exception as e:
            log_error(request, e)
            return redirect('home-list')
    
    def create(self, request):
        log_access(request)
        try:
            mode = request.data.get('mode')
            number = request.data.get('number')
            email = request.data.get('email')
            password = request.data.get('password')

            if mode == 'email':
                user_data = UserData.objects.filter(email=email).first()
            elif mode == 'number':
                user_data = UserData.objects.filter(number=f'+91 {number}').first()
            else:
                return Response({'success': False, 'reason':f'Mode could be "number" or "email" not "{mode}".', 'not_user': False, 'wrong_password': False}, status=status.HTTP_400_BAD_REQUEST)

            if user_data:
                user = authenticate(request, username=user_data.user_id, password=password)

                if user is not None:
                    login(request, user)
                    request.session.set_expiry(30 * 24 * 60 * 60)
                    fun_cart_sync(request=request, user_id=user_data.user_id)
                    
                    # return redirect('account-list')
                    
                    return Response({'success': True}, status=status.HTTP_200_OK)

                else:
                    return Response({'success': False, 'reason':'Wrong password.', 'not_user': False, 'wrong_password': True}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'success': False, 'reason':'Not a user.', 'not_user': True, 'wrong_password': False}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            log_error(request, e)
            return Response({'success': False, 'reason':f'{e}', 'not_user': True, 'wrong_password': False}, status=status.HTTP_400_BAD_REQUEST)

class LogoutViewSet(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            logout(request)
            return redirect('account-list')
            # return Response({'success': True}, status=status.HTTP_200_OK)
        
        except Exception as e:
            log_error(request, e)
            return redirect('account-list')


class AccountView(ViewSet):
    def list(self, request):
        log_access(request)
        try:
            if request.user.is_authenticated:
                user_data = UserData.objects.filter(user_id=request.user).first()
                
                all_order_data = Order.objects.filter(user_id=request.user)
                status_codes = {
                    'UP': 'Unpaid',
                    'PL': 'Order Placed',
                    'IT': 'In Transit',
                    'DV': 'Delivered',
                    }
                all_orders = []
                for order_data in all_order_data:
                    order_id = order_data.order_id
                    temp_order_data = {'order_id':order_id, 'order_date':order_data.order_date_time.strftime("%d %b, %Y"),'order_status':status_codes[order_data.status]}
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
                            'price':item_data.price,
                            'total_price':total_price,
                            'image_1':item_data.image_1.url,
                            'qty':item.qty,
                        })

                    temp_order_data['items'] = all_items
                    temp_order_data['total_price'] = order_total
                    
                    all_orders.append(temp_order_data)
                
                if len(all_orders) == 0:
                    no_order = True
                else:
                    no_order = False                    
                
                data = {
                    'success': True,
                    'user_data':user_data,
                    'all_orders':all_orders,
                    'no_order':no_order,
                    'status': status.HTTP_200_OK,
                }
                
                return render(request, 'UserProfile/account.html', data)

            else:
                return redirect('login-list')
        
        except Exception as e:
            log_error(request, e)
            return redirect('login-list')

class EditAccountDataView(ViewSet):
    def create(self, request):
        log_access(request)
        try:
            if request.user.is_authenticated:
                user_data = UserData.objects.get(user_id=request.user)

                user_data.first_name = request.data.get('first_name')
                user_data.last_name = request.data.get('last_name')
                user_data.primary_address = request.data.get('primary_address')
                user_data.secondary_address = request.data.get('secondary_address')
                user_data.city = request.data.get('city')
                user_data.state = request.data.get('state')
                user_data.country = request.data.get('country')
                user_data.pincode = request.data.get('pincode')
                user_data.save()
                
                return JsonResponse({'success':True})

            else:
                return JsonResponse({'success':False})

        except Exception as e:
            log_error(request, e)
            return JsonResponse({'success':False, 'detail':e})

class ChangePasswordView(ViewSet):
    def list(self,request):
        log_access(request)
        return render(request, 'UserProfile/change_password.html')
    
    def create(self, request):
        log_access(request)
        try:
            number = request.data.get('number')
            number = f'+91 {number}'
            email = request.data.get('email')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            otp_token = request.data.get('otp_token')
            
            if password != confirm_password:
                return Response({'success': False, 'reason':'Password doesnot match.', 'otp_not_verified':False, 'password_doesnot_match':True}, status=status.HTTP_400_BAD_REQUEST)                                
            

            if not Otp.objects.filter(token=otp_token, active=False, number=number).first():
                return Response({'success': False, 'reason':'OTP is not verified.', 'otp_not_verified':True, 'password_doesnot_match':False}, status=status.HTTP_400_BAD_REQUEST)

            user_data = UserData.objects.filter(number=number).first()
            user = User.objects.filter(username=user_data.user_id).first()
            user.set_password(password)
            user.save()
            
            # login(request, user)
            # request.session.set_expiry(30 * 24 * 60 * 60)
            # return redirect('account-list')

            return Response({'success': True}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            log_error(request, e)
            return Response({'success': False, 'reason':f'{e}', 'otp_not_verified':False, 'password_doesnot_match':False}, status=status.HTTP_400_BAD_REQUEST)



def fun_cart_sync(request, user_id):
    try:
        session_token = request.session.get('session_token')
        all_cart = Cart.objects.filter(session_id=session_token)

        for cart_ in all_cart:
            cart_.user_id = user_id

        Cart.objects.bulk_update(all_cart, ['user_id'])
        return True
    except Exception as e:
        log_error(request, e)
        return False

