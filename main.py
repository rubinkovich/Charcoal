import logging
from logging.handlers import RotatingFileHandler
import json
from flask import Flask, render_template, request
import pandas as pd
import requests

TOKEN = ""
CHAT_ID_RUBIN = ""
CHAT_ID_ALEX = ""
CHAT_ID_MAX = ""
CHAT_ID_SVETA = ""


def get_last_order_number():
    with open('last_order_number.txt', 'r') as f:
        return int(f.read().strip())


def set_last_order_number(number):
    with open('last_order_number.txt', 'w') as f:
        f.write(str(number))


def send_telegram_message(text, chats):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    for chat in chats:
        data = {'chat_id': chat, 'text': text}
        response = requests.post(url, data=data)
    return response.json()


# Создание объекта приложения Flask
app = Flask(__name__)

# Настройка логирования
def setup_logging():
    # Создание обработчика, который записывает логи в файл
    handler = RotatingFileHandler('C:/Charcoal order/app.log', maxBytes=10000000, backupCount=3)
    # Определение формата сообщений
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    # Добавление обработчика к регистратору приложения
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

# Вызов функции настройки логирования
setup_logging()

@app.route('/', methods=['GET', 'POST'])
def index():
    price_type = request.args.get('price_type', 'Наличный расчет')  # Получаем тип цены из параметров запроса
    df = pd.read_excel('products.xlsx')  # Чтение файла Excel
    df['Цена'] = df[price_type]  # Устанавливаем цену в соответствии с выбранным типом
    products = df.to_dict('records')  # Преобразование DataFrame в список словарей

    if request.method == 'POST':
        last_order_number = get_last_order_number() + 1  # Увеличиваем номер заказа на единицу
        set_last_order_number(last_order_number)  # Сохраняем новый номер заказа
        customer = request.form.get('customer')
        phone = request.form.get('phone')
        address = request.form.get('address')
        price_type = request.form.get('priceType')
        order = request.form.get('order')
        total_cost = request.form.get('total_cost')
        desired_delivery_date = request.form.get('desiredDate')

        data = json.loads(order)
        order_text = ""
        for item in data:
            order_text += item["name"] + " - " + item["quantity"] + "шт.\n"

        message = (f'Заказ №{last_order_number}\n\n'
                   f'Заказчик: {customer}\n'
                   f'Телефон: {phone}\n'
                   f'Адрес доставки: {address}\n'
                   f'Дата поставки: {desired_delivery_date}\n'
                   f'Оплата: {price_type}\n\n'
                   f'{order_text}\n'
                   f'Общая стоимость заказа: {total_cost}')

        match price_type:  #Формируем список получателей
            case 'Наличный расчет':
                chats = {CHAT_ID_MAX, CHAT_ID_SVETA}
            case 'Без НДС':
                chats = {CHAT_ID_MAX, CHAT_ID_SVETA}
            case 'С НДС':
                chats = {CHAT_ID_MAX, CHAT_ID_SVETA, CHAT_ID_RUBIN}
        if customer == "Test":
            last_order_number = get_last_order_number() - 1   # Уменьшаем номер заказа на единицу,
            set_last_order_number(last_order_number)          # чтобы не сбивать нумерацию при тестах
            chats = {CHAT_ID_ALEX}

        send_telegram_message(message, chats)

    return render_template('index.html', products=products, price_type=price_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
