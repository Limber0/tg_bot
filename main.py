from dataBase import DataBase
from pyqiwip2p import QiwiP2P
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from button import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
FORMAT = "%(asctime)s %(levelname)s - %(message)s"


logger_info = logging.getLogger("INFO")
logger_info.setLevel(level="DEBUG")

handler_info_file = logging.FileHandler("info.log")
handler_info_file.setFormatter(logging.Formatter(FORMAT))
handler_info_file.setLevel(logging.DEBUG)

handler_info = logging.StreamHandler()
handler_info.setFormatter(logging.Formatter(FORMAT))
handler_info.setLevel(logging.DEBUG)

logger_info.addHandler(handler_info_file)
logger_info.addHandler(handler_info)



logger_error = logging.getLogger("WARNING")
logger_error.setLevel(level="WARNING")

handler_error_file = logging.FileHandler("error.log")
handler_error_file.setFormatter(logging.Formatter(FORMAT))
handler_error_file.setLevel(logging.DEBUG)

handler_error = logging.StreamHandler()
handler_error.setFormatter(logging.Formatter(FORMAT))
handler_error.setLevel(logging.DEBUG)

logger_error.addHandler(handler_error_file)
logger_error.addHandler(handler_error)


debug = logger_info.debug
info = logger_info.info
warning = logger_error.warning
error = logger_error.error
critical = logger_error.critical

def log(level, text):
    level(text)





file = open("config.txt")
token_bot = file.readline().strip().replace("token_bot: ", "")
qiwi_public_key = file.readline().strip().replace("qiwi_public_key: ", "")
qiwi_secret_key = file.readline().strip().replace("qiwi_secret_key: ", "")
file.close()
p2p = QiwiP2P(auth_key=qiwi_secret_key)
storage = MemoryStorage()
db = DataBase("dataBase.db")
bot = Bot(token_bot, )
dp = Dispatcher(bot, storage=storage)



@dp.message_handler(commands="start", state=None)
async def commands_start(message):
    log(debug, f"The user used the '/start' command, user_id = {message.from_user.id}")
    if not db.get_user(user_id=message.from_user.id):
        log(info, f"User added to database user_id = {message.from_user.id}")
        db.add_user(user_id=message.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(replenish_balance)
    await bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}.\nЯ - бот для пополнения "
                                                f"баланса.\nНажмите на кнопку, чтобы пополнить баланс.",
                               reply_markup=markup)


@dp.message_handler(commands="admin", state=None)
async def commands_admin(message):
    if db.status.get(message) == "admin":
        log(debug, f"The amin used the '/admin' command, user_id = {message.from_user.id}")
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(users_list, logs, change_balance, ban)
        await bot.send_message(message.chat.id, "Добро пожаловать в панель администратора!", reply_markup=markup)
    else:
        log(warning, f"User access to the admin command was denied, user_id = {message.from_user.id}!")
        await bot.send_message(message.chat.id, "Недостаточно прав.")


@dp.callback_query_handler(text_contains="call_check_payment")
async def button_check_payment(call: types.CallbackQuery):
    log(debug, f"Checking payment status, user_id = {call.from_user.id}")
    bill = str(call.data[18:])
    info_check = db.check.get(check_id=bill)
    if info_check:
        if str(p2p.check(bill_id=bill).status) == "PAID":
            log(info, f"The bill is paid, user_id = {call.from_user.id}, check_id = {bill}, money = {info_check[2]}")
            user_money = db.balance.get(user_id=call.from_user.id)
            money = int(info_check[2])
            db.balance.set(balance=user_money + money, user_id=call.from_user.id)
            await bot.send_message(call.message.chat.id, f"Счет оплачен, ваш баланс {user_money + money} рублей.")
            db.check.delete(check_id=bill)
            log(info, f"User balance replenished, user_id = {call.from_user.id}, balance = {user_money + money}")
        else:
            log(debug, f"Waiting for payment user_id = {call.from_user.id}, check_id = {bill}")
            await bot.send_message(call.message.chat.id, "Ожидание оплаты.", reply_markup=buy_meny(url=info_check[3], bill=bill))
    else:
        log(warning, f"Failed to find account, user_id = {call.from_user.id}, check_id = {bill}")
        await bot.send_message(call.message.chat.id, "Счет не найден.")

@dp.callback_query_handler()
async def callback(call: types.CallbackQuery):
    if call.message:
        if call.data =="call_replenish_balance":
            log(debug, f"The user clicked on the button, user_id = {call.from_user.id}, button = call_replenish_balance")
            await bot.send_message(call.message.chat.id, "Введите сумму, на которую вы хотите пополнить баланс.")
            await Pay.button_replenish_balance.set()

        elif call.data == "call_users_list":
            log(debug, f"The user clicked on the button, user_id = {call.from_user.id}, button = call_users_list")
            await bot.send_message(call.message.chat.id, f"Полный список пользователей:\n\n{db.list_users()}")

        elif call.data == "call_logs":
            log(debug, f"The user clicked on the button, user_id = {call.from_user.id}, button = call_logs")
            dock = open('info.log', "rb")
            await bot.send_document(call.message.chat.id, ("info.log", dock))
            dock.close()
            dock = open('error.log', "rb")
            await bot.send_document(call.message.chat.id, ("error.log", dock))
            dock.close()

        elif call.data == "call_change_balance":
            log(debug, f"The user clicked on the button, user_id = {call.from_user.id}, button = call_change_balance")
            await bot.send_message(call.message.chat.id, "Укажите id пользователя для которого хотите изменить баланс.")
            await Admin.button_change_balance.set()

        elif call.data == "call_banned":
            log(debug, f"The user clicked on the button, user_id = {call.from_user.id}, button = call_banned")
            await bot.send_message(call.message.chat.id, "Укажите id пользователя которого нужно забанить.")
            await Admin.button_banned.set()

@dp.message_handler(state=Pay.button_replenish_balance)
async def pending_payment(message, state):
    try:
        int(message.text)
    except ValueError:
        await bot.send_message(message.chat.id, "Введите число.")
        return
    bill = p2p.bill(amount=message.text, lifetime=5)
    log(info, f"Payment created, user_id = {message.from_user.id}, check_id = {bill.bill_id}, money = {message.text}, url = {bill.pay_url}")
    db.check.create(user_id=message.from_user.id, check_id=bill.bill_id, money=message.text, url=bill.pay_url)
    await bot.send_message(message.chat.id, "Платеж создан.", reply_markup=buy_meny(url=bill.pay_url, bill=bill.bill_id))
    await state.finish()


@dp.message_handler(state=Admin.button_banned)
async def button_banned(message, state):
    db.status.banned(message=message)
    log(info, f"User has been blocked, user_id = {message.text}, admin_id = {message.from_user.id}")
    await bot.send_message(message.chat.id, "Пользователь был заблокирован.")
    await state.finish()


@dp.message_handler(state=Admin.button_change_balance)
async def button_banned(message, state):
    user_id = message.text
    async with state.proxy() as var:
        var["user_id"] = user_id
    await bot.send_message(message.chat.id, "Укажите необходимый баланс.")
    await Admin.button_change_balance2.set()


@dp.message_handler(state=Admin.button_change_balance2)
async def button_banned(message, state):
    async with state.proxy() as var:
        user_id = var["user_id"]
    db.balance.set(balance=message.text, user_id=user_id)
    log(info, f"The user's balance has been changed by the administrator, user_id = {user_id}, admin_id = {message.from_user.id}, balance = {message.text}")
    await bot.send_message(message.chat.id, "Баланс пользователя был изменен.")
    await state.finish()






executor.start_polling(dp)
