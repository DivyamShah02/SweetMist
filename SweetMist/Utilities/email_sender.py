import os
import smtplib
import datetime as dt
from email.mime.text import MIMEText
from configparser import ConfigParser
from SweetMist.settings import BASE_DIR
from email.mime.multipart import MIMEMultipart
from Order.models import Order, OrderItem
from Product.models import Product
from Logs.lg_logger import log_error_simple
from SweetMist.Utilities.encoder import decode_base64

CONFIG_FILEPATH: str = os.path.join(BASE_DIR, "config.ini")
BOT_CONFIG = ConfigParser()
BOT_CONFIG.read(CONFIG_FILEPATH)

SMTP_SERVER = BOT_CONFIG.get('SMTP Creds','smtp_server')
SMTP_PORT = BOT_CONFIG.get('SMTP Creds','smtp_port')
EMAIL = decode_base64(BOT_CONFIG.get('SMTP Creds','email'))
PASSWORD = decode_base64(BOT_CONFIG.get('SMTP Creds','password'))
DOMAIN = BOT_CONFIG.get("Server", "domain")

SMTP_SERVER = 'smtpout.secureserver.net'
SMTP_PORT = 465
EMAIL = 'support@sweetmist.in'
PASSWORD = 'Navkar@108'
DOMAIN = ''

def send_order_success_mail(order_id:str, to_email:str):
    try:
        recipient_email = to_email

        message = MIMEMultipart()            
        message['From'] = f"Sweet Mist <{EMAIL}>"
        message['To'] = recipient_email
        message['Subject'] = '🛍️ Your Order is Confirmed! 🎉'

        body_1 = '''<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Confirmation</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #fff; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; background-color: #fff; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
        <h1 style="color: #6a2249; text-align: center;">&#127881; Order Confirmation &#127881;</h1>
        <p style="color: #333; line-height: 1.6;">Hey there!</p>
        <p style="color: #333; line-height: 1.6;">We're thrilled to let you know that your order has been successfully placed.</p>
        <p style="color: #333; line-height: 1.6;">Here's a summary of your order:</p>

    '''
        
        body_2 = '<ul style="padding: 0; margin: 0; list-style-type: none;">'
        
        item_data = OrderItem.objects.filter(order_id=order_id)
        
        for item in item_data:
            product_data = Product.objects.filter(id=item.product_id).first()
            temp_item = f'''
            <li style="margin-bottom: 10px;"><strong>Item:</strong> {product_data.title}</li>
            <li style="margin-bottom: 10px;"><strong>Quantity:</strong> {item.qty}</li>
            <li style="margin-bottom: 10px;"><strong>Total Price:</strong> ₹ {item.price}</li>
            <hr style="margin-bottom: 20px; border-top: 3px solid #6a2249;">            
            '''
        
            body_2 += temp_item
        
        body_2 += '</ul>' 


        body_3 = f'''<!-- If there are multiple orders, you can repeat the above list for each order -->
        <p style="color: #333; line-height: 1.6;">Need to check your order? No problem! Just click the button below:</p>
        <p style="color: #333; line-height: 1.6; text-align: center; margin-top: 20px;"><a href="{DOMAIN}/order_detail/?order_id={order_id}" style="display: inline-block; padding: 10px 20px; background-color: #6a2249; color: #ffffff; text-decoration: none; border-radius: 5px;">View Your Order</a></p>
        <p style="color: #333; line-height: 1.6;">If you have any questions or concerns, feel free to contact us anytime. We're here to help!</p>
        <p style="color: #333; line-height: 1.6;">Thank you for choosing us!</p>
        <p style="color: #6a2249; line-height: 1.6;"><b>Best regards,<br>Sweet Mist</b></p>
    </div>
    </body>
    </html>'''
        
        body = body_1 + body_2 + body_3
        message.attach(MIMEText(body, 'html'))
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, recipient_email, message.as_string())
        
        return True
    
    except Exception as e:
        log_error_simple(e)
        return False

def send_otp_mail(otp:str, to_email:str):
    try:
        recipient_email = to_email

        message = MIMEMultipart()            
        message['From'] = f"Sweet Mist <{EMAIL}>"
        message['To'] = recipient_email
        message['Subject'] = '🔐 Your OTP for Email Verification'

        body = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verification</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f3f3f3; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; background-color: #fff; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
        <h1 style="color: #6a2249; text-align: center;">OTP Verification</h1>
        <p style="color: #333; line-height: 1.6; text-align: center;">Please use the following OTP code to verify your email:</p>
        <div style="font-size: 24px; text-align: center; padding: 20px; background-color: #6a2249; color: #ffffff; border-radius: 5px;">{otp}</div>
        <p style="color: #333; line-height: 1.6; text-align: center;">This OTP code is valid for a single use and will expire in a short time.</p>
        <hr style="border-top: 2px solid #6a2249;">
        <p style="color: #888; text-align: center;">Copyright &copy; 2024 Sweet Mist. All rights reserved.</p>
    </div>
</body>
</html>
'''

        message.attach(MIMEText(body, 'html'))
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, recipient_email, message.as_string())
        
        return True

    except Exception as e:
        log_error_simple(e)
        return False
