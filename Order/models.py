from django.db import models
from django.utils import timezone


# Create your models here.
class Cart(models.Model):
    '''Cart Model'''
    user_id = models.CharField(max_length=10,null=True)
    session_id = models.CharField(max_length=255,null=True)
    product_id = models.CharField(max_length=10,null=True)
    
    qty = models.CharField(max_length=10,null=True)    
    add_date = models.DateTimeField(default=timezone.now,null=True)
    active = models.BooleanField(default=True)
    
class Order(models.Model):
    '''Order Model'''
    user_id = models.CharField(max_length=10)
    order_id = models.CharField(max_length=10)
    order_date_time = models.DateTimeField(default=timezone.now,null=True)
    active = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    
    STATUS_CHOICES = (
        ('UP', 'Unpaid'),
        ('PL', 'Order Placed'),
        ('IT', 'In Transit'),
        ('DV', 'Delivered'),
        # ('OS', 'Other Status'),
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='UP')

    shipment = models.BooleanField(default=False)
    # payment_id = models.CharField(max_length=15)
    
    paid = models.BooleanField(default=False)
    payment_session_id = models.CharField(max_length=255)
    pg_order_id = models.CharField(max_length=255)
    pg_order_status = models.CharField(max_length=255)
    pg_payment_id = models.CharField(max_length=255)
    pg_payment_group = models.CharField(max_length=255, null=True)
    


class OrderItem(models.Model):
    '''Order Item Model'''
    order_id = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    qty = models.CharField(max_length=10)
    price = models.CharField(max_length=30)
    per_item_price = models.CharField(max_length=30)
