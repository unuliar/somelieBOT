# -*- coding: utf-8 -*-

import telebot;
bot = telebot.TeleBot('891676728:AAEl_6OWG86_g2o39tLZMoHP3V36OJDlyGo')

import requests
import telebot
from telebot import types
import config
import dbworker
from bs4 import BeautifulSoup


def get_wine_rating(message):
    bot.send_message(message.chat.id, "Введите минимальную оценку для вина")


def get_wine_price(message):
    bot.send_message(message.chat.id, "Введите ценовой диапазон в формате мин-макс")


def get_wine_type(message):
    keyboard = types.InlineKeyboardMarkup()
    key_red = types.InlineKeyboardButton(text='Красное', callback_data='red') 
    keyboard.add(key_red)
    key_white = types.InlineKeyboardButton(text='Белое', callback_data='white')
    keyboard.add(key_white)
    bot.send_message(message.from_user.id, text="Какое вино хочешь найти?", reply_markup=keyboard)

def get_rating(message):
    bot.send_message(message.chat.id, "Введите минимальный рейтинг от 1 до 5, к примеру, 4.6")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "red":
        dbworker.add_to_end(str(call.message.chat.id) + '_data', '?wine_type_ids[]=1')
        bot.send_message(call.message.chat.id, 'Отличный выбор!')
    elif call.data == "white":
        dbworker.add_to_end(str(call.message.chat.id) + '_data', '?wine_type_ids[]=2')
        bot.send_message(call.message.chat.id, 'Отличный выбор!')
    dbworker.set_state(call.message.chat.id, config.States.S_ENTER_WINE_PRICE.value)
    get_wine_price(call.message)


@bot.message_handler(commands=["start"])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)
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


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой")
    dbworker.set_state(message.chat.id, '-1')
    dbworker.set_state(str(message.chat.id) + '_data', '')


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_WINE_PRICE.value)
def user_entering_price(message):
    price = message.text.split('-')
    if (not price[0].isdigit()) or (not price[1].isdigit()):
        bot.send_message(message.chat.id, "Неверно указана цена")
        return
    dbworker.set_state(message.chat.id, config.States.S_ENTER_WINE_RATING.value)
    dbworker.add_to_end(str(message.chat.id) + '_data', '&price_range_max=' + price[0] + '&price_range_min=' + price[1])
    get_rating(message)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_WINE_RATING.value)
def user_entering_rating(message):
    dbworker.add_to_end(str(message.chat.id) + '_data', '&min_rating=' + message.text)
    bot.send_message(message.chat.id, get_wine_from_api(dbworker.get_current_state(str(message.chat.id)+'_data')))

@bot.message_handler(content_types=['text'])
def start(message):
    bot.send_message(message.from_user.id, dbworker.get_current_state(message.chat.id))
    if message.text == '/start':
        bot.send_message(message.from_user.id, "PRIVET")
        get_wine_type(message)
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')

def get_wine_from_api(paramsstr):
    URL = "https://vivino.com/explore"
    r = requests.get(url = URL+paramsstr, headers = {'User-agent': 'vin 0.1'}, timeout=10000)
    print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    for wine in soup.select('div[class*=explorerCard__explorerCard]'):
        print(wine.get_text())
    return URL+paramsstr


bot.polling(none_stop=True, interval=0)
