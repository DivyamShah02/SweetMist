from django.contrib import admin
from .models import UserData,Otp

# Register your models here.

class AdminUserData(admin.ModelAdmin):
    list_display = ('user_id','email','number','first_name','last_name','join_date')
admin.site.register(UserData,AdminUserData)

class AdminOtp(admin.ModelAdmin):
    list_display = ('user_id','session_id','otp','create_date','active')
admin.site.register(Otp,AdminOtp)

