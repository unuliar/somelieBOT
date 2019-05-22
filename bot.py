# -*- coding: utf-8 -*-

import telebot
import requests
import json
from telebot import types
import config
import dbworker
from api_vivino import *

bot = telebot.TeleBot(config.token)

def get_wine_rating(message):
    bot.send_message(message.chat.id, "Введите минимальную оценку для вина")


def get_wine_price(message):
    bot.send_message(message.chat.id, "Введите ценовой диапазон в формате мин-макс. К примеру 1500-2000")


def get_wine_type(message):
    keyboard = types.InlineKeyboardMarkup()
    key_red = types.InlineKeyboardButton(text='Красное', callback_data='red')
    keyboard.add(key_red)
    key_white = types.InlineKeyboardButton(text='Белое', callback_data='white')
    keyboard.add(key_white)
    bot.send_message(message.from_user.id, text="Какое вино хотите найти?", reply_markup=keyboard)


def get_rating(message):
    bot.send_message(message.chat.id, "Введите минимальный рейтинг от 1 до 5, к примеру, 4.6")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "red":
        dbworker.add_to_end(str(call.message.chat.id) + '_data', '&wine_type_ids[]=1')
        bot.send_message(call.message.chat.id, 'Отличный выбор!')
    elif call.data == "white":
        dbworker.add_to_end(str(call.message.chat.id) + '_data', '&wine_type_ids[]=2')
        bot.send_message(call.message.chat.id, 'Отличный выбор!')
    elif call.data == "other":
        get_wine_from_api(call.message, config.static_params + dbworker.get_current_state(str(call.message.chat.id) + '_data'))
        return 0
    elif call.data == "reset":
        cmd_reset(call.message)
        return 0
    dbworker.set_state(call.message.chat.id, config.States.S_ENTER_WINE_PRICE.value)
    get_wine_price(call.message)


@bot.message_handler(commands=["start"])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)

    #print(state)
    if state == config.States.S_ENTER_WINE_TYPE.value:
        bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить тип вина :( Жду...")
    elif state == config.States.S_ENTER_WINE_PRICE.value:
        bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить диапазон цен :( Жду...")
    elif state == config.States.S_ENTER_WINE_RATING.value:
        bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить рейтинг  Жду...")
    elif state == '-1':
        start(message)
    else:
        dbworker.set_state(message.chat.id, config.States.S_ENTER_WINE_TYPE.value)
        get_wine_type(message)


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой")
    dbworker.set_state(str(message.chat.id), "-1")
    dbworker.set_state(str(message.chat.id) + '_data', '')
    dbworker.set_state(str(message.chat.id) + '_num', '')
    cmd_start(message)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_WINE_PRICE.value)
def user_entering_price(message):
    price = message.text.split('-')

    if ((len(price) != 2) or not price[0].isdigit()) or (not price[1].isdigit()):
        bot.send_message(message.chat.id, "Неверно указана цена")
        return
    dbworker.set_state(message.chat.id, config.States.S_ENTER_WINE_RATING.value)
    dbworker.add_to_end(str(message.chat.id) + '_data', '&price_range_min=' + price[0] + '&price_range_max=' + price[1])
    get_rating(message)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_WINE_RATING.value)
def user_entering_rating(message):
    if message.text.isdigit:
        if float(message.text) > 0 and float(message.text) < 5:
            dbworker.add_to_end(str(message.chat.id) + '_data', '&min_rating=' + message.text)
            get_wine_from_api(message, config.static_params + dbworker.get_current_state(str(message.chat.id) + '_data'))
            return
    bot.send_message(message.chat.id, 'Неверно указан рейтинг')



@bot.message_handler(content_types=['text'])
def start(message):
    #bot.send_message(message.from_user.id, dbworker.get_current_state(message.chat.id))
    if message.text == '/start':
        bot.send_message(message.chat.id, "Доброго времени суток")
        get_wine_type(message)
    else:
        bot.send_message(message.chat.id, 'Напишите /start')


def get_wine_from_api(message, params):
    wines = get_wines(get_session_key(), params)
    viewed = update_viewed_counter(message)
    if viewed >= len(wines):
        bot.send_message(message.chat.id, 'Нет вина и это не наша вина(( /reset')
        return ''
    wine = wines[viewed]
    text = f'Вино {wine.name} год. Цена {wine.price} рублей. Оценка {wine.stat}. Объём {wine.volume} мл.'

    markup = types.InlineKeyboardMarkup()
    url = f'https://www.vivino.com/{wine.seo_name}/w/{wine.id}?year={wine.year}'
    btn_link = types.InlineKeyboardButton(text='Подробнее', url=url)
    btn_other = types.InlineKeyboardButton(text='Другой вариант', callback_data='other')
    btn_reset = types.InlineKeyboardButton(text='Начать сначала', callback_data='reset')

    markup.add(btn_link)
    markup.add(btn_other)
    markup.add(btn_reset)
    bot.send_photo(message.chat.id, 'http:' + wine.image_link, caption=text, reply_markup=markup)
    return ''

def update_viewed_counter(message):
    curr = dbworker.get_current_state(str(message.chat.id) + '_num')
    if len(curr) > 0:
        curr = int(curr) + 1
    else:
        curr = 0
    dbworker.set_state(str(message.chat.id) + '_num', curr)
    return curr


bot.polling(none_stop=True, interval=0)

