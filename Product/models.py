from django.db import models
from django.utils import timezone

# Create your models here.

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    sku = models.CharField(max_length=10)
    category = models.CharField(max_length=100)
    tags = models.CharField(max_length=255)
    info = models.TextField()
    
    no_of_item = models.CharField(max_length=4, null=True, blank=True)
    per_item_weight = models.CharField(max_length=255, null=True, blank=True)
    total_weight = models.CharField(max_length=255, null=True, blank=True)

    price = models.CharField(max_length=30) #actual selling price
    high_price = models.CharField(max_length=30) #high price that will be canceled
    discounted_price = models.CharField(max_length=30, null=True, blank=True) #total amt of discount
    discount_rate = models.CharField(max_length=3, null=True, blank=True) #rate of discount
    
    cost_price = models.CharField(max_length=30 ,null=True, blank=True) #cost price wont be shown on website    

    image_1 = models.ImageField(upload_to='Product_Img')
    image_2 = models.ImageField(upload_to='Product_Img')
    image_3 = models.ImageField(upload_to='Product_Img')
    image_4 = models.ImageField(upload_to='Product_Img')
    image_5 = models.ImageField(upload_to='Product_Img')
    cart_image = models.ImageField(upload_to='Product_Img')
    add_date = models.DateTimeField(default=timezone.now)
    
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.slug

class Category(models.Model):
    category = models.CharField(max_length=100,null=True)

