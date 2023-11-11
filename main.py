import telebot
from telebot import types
import os
from PIL import Image
import pickle
import time
import asyncio
import requests
import json
import g4f

APIKEY = 'c9aeaddddca1ad702e4c71713135a70e'
user_data_dir = os.path.abspath('data\\user_data.txt')

def get_weather(lat, lon):
    weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={APIKEY}&units=metric')
    weather = json.loads(weather_response.text)
    print(weather)
    temp = weather['main']['temp']
    rain = weather['weather'][0]['main']
    return [temp, rain]

def gpt(text, weather):
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOTYyZDkxZDktZTFiOC00YjVlLWJiNjktYzlmYzFiNmMzMmEwIiwidHlwZSI6ImFwaV90b2tlbiJ9.MnpC2h9x7Kl6-SMVUdrmA9xj8c326q4ZCP-A0V9qt3U"}
    url = "https://api.edenai.run/v2/text/generation"
    payload = {"providers": "openai,cohere",
               "text": f"generate clothes for situation? when on the street 1,62 degrees and clouds, write it on russian language",
               "temperature": weather[0],
               "max_tokens": 250}
    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    return result['openai']['generated_text']

def create_markup(message, msg, texts, callbacks, rw=3, edit=False, markup=True):
    markup = types.InlineKeyboardMarkup(row_width=rw)
    for i in range(len(texts)):
        item = types.InlineKeyboardButton(text=texts[i], callback_data=str(callbacks[i]))
        markup.add(item)
    if edit == False:
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    if edit == True and markup==True:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=msg, reply_markup=markup)
    if edit == True and markup==False:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=msg)




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
                      ["Мужчина", "Женщина", 'Программист'], ['мужчина', 'женщина', 'программист'], edit=True)






    if call.data == 'геолокация':
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(call.message.chat.id, "Поделись местоположением", reply_markup=keyboard)


    if call.data == 'одежда':
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text="Меню", callback_data=str('меню'))
        markup.add(item1)
        bot.send_message(call.message.chat.id, 'Одежда на сегодня:\nВоздух еще не прогрелся, а холодный '
                                               'ветер норовит отправить тебя на больничный — не надо так! '
                                               'Поэтому мы выбираем миди-пальто с «глухими» лонгсливами и '
                                               'достаточно плотными брюками. Будет жарко — можно расстегнуть'
                                               ' верхний слой.Еще одна небанальная идея — совместить кожанку'
                                               ' и дубленку. Благодаря многослойности тепло сохранится, а '
                                               'ты сможешь снять один из слоев, если вдруг станет жарко.', reply_markup=markup)

@bot.message_handler(content_types=['location'])
def location (message):
    if not (message.location is None):
        weather = list(get_weather(message.location.latitude, message.location.longitude))
        print(weather)
        bot.send_message(message.chat.id, f'{weather[0]}\n{weather[1]}')

while True:
    try:
        bot.polling(none_stop=True)
    except:
        time.sleep(1)