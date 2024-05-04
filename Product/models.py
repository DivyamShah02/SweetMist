from django.db import models
from django.utils import timezone

# Create your models here.

class Product(models.Model):
    title = models.CharField(max_length=255,null=True)
    slug = models.SlugField(max_length=255,unique=True,null=True)
    sku = models.CharField(max_length=10,null=True)
    category = models.CharField(max_length=100,null=True)
    tags = models.CharField(max_length=255,null=True)
    info = models.TextField(null=True)

    price = models.CharField(max_length=30,null=True) #actual selling price
    high_price = models.CharField(max_length=30,null=True) #high price that will be canceled
    discounted_price = models.CharField(max_length=30,null=True) #total amt of discount
    discount_rate = models.CharField(max_length=3,null=True) #rate of discount

    image_1 = models.ImageField(upload_to='Product_Img',null=True)
    image_2 = models.ImageField(upload_to='Product_Img',null=True)
    image_3 = models.ImageField(upload_to='Product_Img',null=True)
    image_4 = models.ImageField(upload_to='Product_Img',null=True)
    image_5 = models.ImageField(upload_to='Product_Img',null=True)
    cart_image = models.ImageField(upload_to='Product_Img',null=True)
    add_date = models.DateTimeField(default=timezone.now,null=True)
    
    def __str__(self):
        return self.slug

class Category(models.Model):
    category = models.CharField(max_length=100,null=True)

