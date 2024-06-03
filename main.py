
import json
from flask import Flask, render_template, request
import pandas as pd
import requests

TOKEN = "7059904287:AAFFpELPxz8WDC0q29tuDWD6oQkCNSs-FTo"
CHAT_ID = "133536406"

def get_last_order_number():
    with open('last_order_number.txt', 'r') as f:
        return int(f.read().strip())

def set_last_order_number(number):
    with open('last_order_number.txt', 'w') as f:
        f.write(str(number))

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': text}
    response = requests.post(url, data=data)
    return response.json()

app = Flask(__name__)

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

        data = json.loads(order)
        order_text = ""
        for item in data:
            order_text += item["name"] + " - " + item["quantity"] + "шт.\n"

        message = (f'Заказ №{last_order_number}\n\n'
                   f'Заказчик: {customer}\n'
                   f'Телефон: {phone}\n'
                   f'Адрес доставки: {address}\n'
                   f'Оплата: {price_type}\n\n'
                   f'{order_text}\n'
                   f'Общая стоимость заказа: {total_cost}')
        send_telegram_message(message)

    return render_template('index.html', products=products, price_type=price_type)

if __name__ == '__main__':
    app.run(debug=True)