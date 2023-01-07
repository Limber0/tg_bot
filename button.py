from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class Admin(StatesGroup):
    button_users_list = State()
    button_logs = State()
    button_change_balance = State()
    button_change_balance2 = State()
    button_banned = State()

""" Кнопки админки """
users_list = types.InlineKeyboardButton("Пользователи", callback_data="call_users_list")
logs = types.InlineKeyboardButton("Логи", callback_data="call_logs")
change_balance = types.InlineKeyboardButton("Изменить баланс ", callback_data="call_change_balance")
ban = types.InlineKeyboardButton("Выдать бан ", callback_data="call_banned")

class Pay(StatesGroup):
    button_replenish_balance = State()
    # button_check_payment = State()

""" Кнопки бота"""
replenish_balance = types.InlineKeyboardButton("Пополнить баланс", callback_data="call_replenish_balance")
def buy_meny(url, bill):
    qiwiMenu = types.InlineKeyboardMarkup(row_width=2)
    payment_link = types.InlineKeyboardButton("Ссылка на оплату.", url=url)
    qiwiMenu.insert(payment_link)
    check_payment = types.InlineKeyboardButton("Проверить", callback_data="call_check_payment"+bill)
    qiwiMenu.insert(check_payment)
    return qiwiMenu