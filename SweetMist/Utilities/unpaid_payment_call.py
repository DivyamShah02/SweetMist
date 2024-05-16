import requests

url = 'https://www.sweetmist.in/order/check_unpaid_payment/'

response = requests.get(url)
print(response.text)
