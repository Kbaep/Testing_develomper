import requests
from xml.etree import ElementTree as ET
from time import sleep
from config import chat_id


def currency_value_in_rub(balance, data):
    ''' Перевод валюту в рубли '''

    info = requests.get(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={data}')
    structure = ET.fromstring(info.content)
    dollar = structure.find("./*[@ID='R01235']/Value")
    one_dollar = float(dollar.text.replace(',', '.'))
    value_in_rub = balance * one_dollar
    return round(value_in_rub, 2)


def send_msg(text):
    '''Отправка сообщения в Telegram'''

    token = '1769659001:AAFXvz4eCD9AnGSN-TEG4UkDF9fmw9mWwLs'
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
    r = requests.get(url_req)
    print(r.json())
    sleep(4)
