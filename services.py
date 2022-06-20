import os
from time import sleep
from xml.etree import ElementTree as ET

import dotenv
import requests

dotenv.load_dotenv('.env')


def currency_value_in_rub(balance, date):
    ''' Перевод валюту в рубли. При подключении к ЦБРФ,
     получаем данные в формате XML и находим USD по ID = R01235.'''

    info = requests.get(
        f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={date}')
    structure = ET.fromstring(info.content)
    dollar = structure.find("./*[@ID='R01235']/Value")
    one_dollar = float(dollar.text.replace(',', '.'))
    value_in_rub = balance * one_dollar
    return round(value_in_rub, 2)


def send_msg(text: str):
    '''Отправка сообщения в Telegram, через подключение по API.
    В конце используется 4 секундный сон, т.к.
     в минуту можно отправлять только 20 сообщений.
    В token, передаётся информация о бот token. В chat_id,
     передаётся информация об ID чата,
     в который будет отправляться сообщение
    '''
    token = os.environ.get('TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + \
              "?chat_id=" + chat_id + "&text=" + text
    requests.get(url_req)
    sleep(4)
