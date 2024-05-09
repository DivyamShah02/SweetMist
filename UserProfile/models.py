from django.db import models
from django.utils import timezone

# Create your models here.

class UserData(models.Model):
    user_id = models.CharField(max_length=10,null=True,unique=True)
    email = models.EmailField(null=True)
    password = models.CharField(max_length=255,null=True,default='NULL')
    number = models.CharField(max_length=15,null=True)
    first_name = models.CharField(max_length=255,null=True)
    last_name = models.CharField(max_length=255,null=True)
    join_date = models.DateTimeField(default=timezone.now,null=True)
    
    primary_address = models.TextField(null=True) # flat number & society
    secondary_address = models.TextField(null=True) # street address
    city = models.CharField(max_length=100,null=True)
    state = models.CharField(max_length=100,null=True)
    country = models.CharField(max_length=100,null=True)
    pincode = models.CharField(max_length=10,null=True)


class Otp(models.Model):
    user_id = models.CharField(max_length=10,null=True, blank=True)
    session_id = models.CharField(max_length=255,null=True, blank=True)
    otp = models.CharField(max_length=6)
    number = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    attempts = models.IntegerField(default=0)
    create_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    token = models.CharField(max_length=255,default='Null')
        
