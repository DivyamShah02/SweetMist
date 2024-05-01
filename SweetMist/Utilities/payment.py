import os
import pdb
import json
import requests
from SweetMist.Utilities.encoder import decode_base64
from configparser import ConfigParser
from SweetMist.settings import BASE_DIR
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.order_meta import OrderMeta
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.create_order_request import CreateOrderRequest


CONFIG_FILEPATH: str = os.path.join(BASE_DIR, "config.ini")
BOT_CONFIG = ConfigParser()
BOT_CONFIG.read(CONFIG_FILEPATH)

CLIENT_ID = decode_base64(BOT_CONFIG.get("Payment Gateway", "client_id"))
CLIENT_SECRET = decode_base64(BOT_CONFIG.get("Payment Gateway", "client_secret"))
API_VERSION = BOT_CONFIG.get("Payment Gateway", "api_version")
DOMAIN = BOT_CONFIG.get("Server", "domain")


def create_pg_order(order_id:str, customer_id:str,customer_name, customer_email, customer_phone:str, order_amount, order_currency='INR'):
    url = "https://api.cashfree.com/pg/orders"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-version": API_VERSION,
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET
    }
    data = {
        "customer_details": {
            "customer_id": customer_id,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "customer_name": customer_name
        },
        "order_meta": {
            "return_url": f"{DOMAIN}/order_detail/?order_id={order_id}&order_placed=True"
        },
        "order_id": order_id,
        "order_amount": order_amount,
        "order_currency": order_currency
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return True, response.json()
    
    else:
        return False, response.json()

def create_pg_order_old(order_id, customer_id:str,customer_name, customer_email, customer_phone:str, order_amount, order_currency='INR'):
    try:
        Cashfree.XClientId = CLIENT_ID
        Cashfree.XClientSecret = CLIENT_SECRET
        x_api_version = API_VERSION
        Cashfree.XEnvironment = Cashfree.PRODUCTION
        customerDetails = CustomerDetails(customer_id=customer_id, customer_phone=customer_phone, customer_email=customer_email, customer_name=customer_name)
        createOrderRequest = CreateOrderRequest(order_id=order_id, order_amount=order_amount, order_currency=order_currency, customer_details=customerDetails)
        orderMeta = OrderMeta()
        orderMeta.return_url = f"{DOMAIN}/order_detail/?order_id={order_id}&order_placed=True"
        createOrderRequest.order_meta = orderMeta
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        order_json = json.loads(api_response.data.json())
        return True, order_json

    except Exception as e:
        return False, e

def check_payment(order_id):
    try:
        Cashfree.XClientId = CLIENT_ID
        Cashfree.XClientSecret = CLIENT_SECRET
        x_api_version = API_VERSION
        Cashfree.XEnvironment = Cashfree.PRODUCTION
        api_response_payment_1 = Cashfree().PGOrderFetchPayments(x_api_version, order_id, None)
        payment_data_json = json.loads(api_response_payment_1.data[0].json())
        return True, payment_data_json
    except Exception as e:
        return False, e

def get_payment_details(order_id, pg_payment_id=None):
    try:
        XClientId = CLIENT_ID
        XClientSecret = CLIENT_SECRET
        x_api_version = API_VERSION
        headers = {
            'x-client-id':XClientId,
            'x-partner-apikey':XClientSecret,
            'x-api-version':x_api_version,
            'Content-Type': 'application/json',
        }
        if pg_payment_id:
            url = f'https://api.cashfree.com/pg/orders/{order_id}/payments/{pg_payment_id}'
        
        else:
            url = f'https://api.cashfree.com/pg/orders/{order_id}/payments'
        
        response = requests.get(url,headers=headers)
        response_data = response.json()
        if response.status_code == 200:
            if type(response_data) == list:
                if len(response_data) == 0:
                    return True, {'payment_status':'PENDING', 'is_captured':False}
                else:
                    for pay_data in response_data:
                        if pay_data['is_captured']:
                            return True, pay_data

                    return True, {'payment_status':'PENDING', 'is_captured':False}

            return True, response_data

        else:
            return False, response_data

    except Exception as e:
        return False, e


# done,data = create_pg_order(
# order_id = '182565895459',
# order_amount = 100,
# customer_email = 'divyamshah123@gsres.com',
# customer_name = 'Divyam Shah',
# customer_id = '1234567890',
# customer_phone = '9054413199'
# )

# pdb.set_trace()

# pay_da = check_payment(order_id='7881184365')
# done, data = get_payment_details(order_id='7881184365')
# pdb.set_trace()

# pdb.set_trace()
# print(data)

