import telebot
from telebot import types
import os
from PIL import Image
import pickle
import time
import random
import requests
import json
import g4f

APIKEY = 'c9aeaddddca1ad702e4c71713135a70e'
user_data_dir = os.path.abspath('data\\user_data.txt')
weather = {}

def get_weather(lat, lon):
    weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={APIKEY}&units=metric')
    weather = json.loads(weather_response.text)
    temp = weather['main']['temp']
    rain = weather['weather'][0]['main']
    return [temp, rain]

def gpt(gender, weather, preferences):
    gen = ''
    if gender == 'мужчина':
        gen = 'for man'
    if gender == 'женщина':
        gen = 'for man'
    if gender == 'программист':
        gen = 'and yellow car'
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOTYyZDkxZDktZTFiOC00YjVlLWJiNjktYzlmYzFiNmMzMmEwIiwidHlwZSI6ImFwaV90b2tlbiJ9.MnpC2h9x7Kl6-SMVUdrmA9xj8c326q4ZCP-A0V9qt3U"}
    url = "https://api.edenai.run/v2/text/generation"
    payload = {"providers": "openai,cohere",
               "text": f"generate clothes{gen} for situation, when on the street {weather[0]} degrees and {weather[1]} according to preferences: {preferences}, write it on russian language",
               "temperature": weather[0],
               "max_tokens": 250}
    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    return result['openai']['generated_text']

def create_markup(message, msg, texts, callbacks, rw=3, edit=False, markup_=True):
    markup = types.InlineKeyboardMarkup(row_width=rw)
    for i in range(len(texts)):
        item = types.InlineKeyboardButton(text=texts[i], callback_data=str(callbacks[i]))
        markup.add(item)
    print(edit)
    print(markup_)
    if edit == False:
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    if edit == True and markup_ == True:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=msg, reply_markup=markup)
    if edit == True and markup_ == False:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=msg, reply_markup=markup)
    else:
        print('f')




token='6513993150:AAGo6g3e3_i6559wCJ6iKeTBF9IoWbeKk-8'
bot=telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def button_message(message):
    create_markup(message, 'Приветствуем в боте!', ['Настройки', 'Одежда на сегодня'], ['настройки', 'геолокация'])

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'меню':
        create_markup(call.message, 'Выберите то, что вам нужно', ["Выбор предпочтений",
        "Одежда на сегодня"],['предпочтения', 'геолокация'])

    if call.data == 'настройки':
        create_markup(call.message, 'Настройте всё по вашим предпочтениям.', ["Пол",
        "Предпочтения в одежде"], ['пол', 'предпочтения'])

    if call.data == 'пол':
        with open(user_data_dir, 'rb') as filehandle:
            usr_data = pickle.load(filehandle)
        if call.message.from_user.id in usr_data['gender']:
            choosen = '\nВыбран:'+usr_data['gender'][call.message.from_user.id]
        else:
            choosen = '\n Не выбран'
        create_markup(call.message, 'Укажите ваш пол, чтобы мы могли корректно подобрать одежду для вас'+choosen, ["Мужчина",
        "Женщина", 'Программист'], ['мужчина', 'женщина', 'программист'])

    if call.data == 'мужчина' or call.data == 'женщина' or call.data == 'программист':
        with open(user_data_dir, 'rb') as filehandle:
            usr_data = pickle.load(filehandle)
        usr_data['gender'][call.message.from_user.id] = call.data
        with open(user_data_dir, 'wb') as filehandle:
            pickle.dump(usr_data, filehandle)
        if call.message.from_user.id in usr_data['gender']:
            choosen = '\nВыбран:'+usr_data['gender'][call.message.from_user.id]
        else:
            choosen = '\n Не выбран'
        create_markup(call.message, 'Укажите ваш пол, чтобы мы могли корректно подобрать одежду для вас' + choosen,
                      ["Мужчина", "Женщина", 'Программист'], ['мужчина', 'женщина', 'программист'], edit=True, markup_=False)

    if call.data == 'геолокация':
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(call.message.chat.id, "Поделись местоположением", reply_markup=keyboard)

    if call.data == 'одежда':
        create_markup(call.message.chat.id, 'gpt не работает', ['Меню'], ['меню'])
        # gpt(usr_data['gender'][call.message.from_user.id], weather=weather[call.message.from_user.id], preferences=usr_data['preferences'][call.message.from_user.id])

@bot.message_handler(content_types=['location'])
def location (message):
    if not (message.location is None):
        weather[message.from_user.id] = list(get_weather(message.location.latitude, message.location.longitude))
        print(int(weather[message.from_user.id][0]))
        if int(weather[message.from_user.id][0]) < -15:
            clothes={1:['валенки', 'тёплые сапоги'], 2:['джинсы с начёсом', 'тёплые штаны'], 3: ['Тёплую куртку', 'кофту и куртку'], 4: ['Шапку из шерсти', 'Шапку ушанку']}
        elif int(weather[message.from_user.id][0]) > -15 and int(weather[message.from_user.id][0]) < -0:
            clothes={1:['утеплённая обувь', 'осенние сапоги'], 2:['джинсы с начёсом', 'брюки с начёсом'], 3: ['пальто', 'кофту'], 4: ['шапку', 'шарф']}
        elif int(weather[message.from_user.id][0]) > 0 and int(weather[message.from_user.id][0]) < 15:
            clothes = {1: ['кросовки', 'туфли с утеплёнными носками'], 2: ['брюки', 'джинсы'],
                       3: ['пальто', 'лёгкую кофту'], 4: ['лёгкую шапку', 'капюшон']}
        elif int(weather[message.from_user.id][0]) > 15 and int(weather[message.from_user.id][0]) < 30:
            clothes = {1: ['сандали', 'кроксы'], 2: ['шорты', 'спортивные штаны'],
                       3: ['футболка', 'майку'], 4: ['панамку', 'солнечные очки']}
        else:
            clothes = {1:['не идите на улицу', 'не идите на улицу'],2:['Не Идите На улицу', 'не идите на улицу'],3:['Не ИдИтЕ нА уЛиЦу', 'не идите на улицу'],4:['НЕ ИДИТЕ НА УЛИЦУ!', 'не идите на улицу']}
        cloth = [clothes[1][random.randint(0,1)], clothes[2][random.randint(0,1)], clothes[3][random.randint(0,1)], clothes[4][random.randint(0,1)]]
        msgg = str(f'Cегодня вам стоит надеть: \n1.{cloth[0]}\n2.{cloth[1]} \n3.{cloth[2]}\n4.{cloth[3]} \nтак как сегодня на улице {weather[message.from_user.id][0]} градуса')
        print(msgg)
        bot.send_message(message.chat.id, msgg)


while True:
    try:
        bot.polling(none_stop=True)
    except:
        time.sleep(1)