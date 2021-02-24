import telebot
import os
from flask import Flask, request
import Backend as bk
import datetime
import time_my as mt
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

server = Flask(__name__)


bot = telebot.TeleBot('token')

keyboard_week = telebot.types.ReplyKeyboardMarkup()
keyboard_week.row('Понедельник')
keyboard_week.row('Вторник')
keyboard_week.row('Среда')
keyboard_week.row('Четверг')
keyboard_week.row('Пятница')
keyboard_week.row('Главное меню')

keyboard_func = telebot.types.ReplyKeyboardMarkup()
keyboard_func.row('Пары сегодня')
keyboard_func.row('Пары на завтра')
keyboard_func.row('Пары на каждый день недели')
keyboard_func.row('Какая идет неделя?')
keyboard_func.row('Календарь')

dn = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6, 'Воскресенье': 7,
      'Воскресенье': 0}

com = ['Пары сегодня', 'Пары на каждый день недели', 'Какая идет неделя?', 'Сменить группу', 'Главное меню', '/start',
       '/all', 'Календарь', 'Начало периода:', 'Пары на завтра']


# После команды /all с моего id отсылает сообщение всем пользователям бота
@bot.message_handler(func=lambda message: message.chat.id == 304032023 and message.text[:4] == '/all')
def start_message(message):
    ids = bk.messages_id()
    for id in ids:
        bot.send_message(id, message.text[4:])


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, чтобы узнать расписание введи название группы, например "ЭРС-19-2"'
                     + u'\U00002935')


@bot.message_handler(func=lambda message: message.text not in com and message.text not in dn)
def check_group(message):
    group = str(message.text)
    group_id = bk.get_group_id(group)
    if group_id == 'Ошибка, такой группы нет':
        bot.send_message(message.chat.id, 'Ошибка, такой группы нет, введи группу снова')
    else:
        bk.izm(str(message.chat.id), str(message.text))
        bot.send_message(message.chat.id,
                         'Можешь посмотреть свое расписание на завтра или на следующий день с помощью кнопок внизу \n'
                         'Чтобы сменить группу, просто введи название другой группы\n',
                         reply_markup=keyboard_func)


@bot.message_handler(func=lambda mess: mess.text == 'Пары сегодня')
def send_today(message):
    group_id = bk.output(message.chat.id)
    start_time = datetime.datetime.today().strftime("%Y.%m.%d")
    s = bk.get_schedule(str(group_id), start_time, start_time)
    bot.send_message(message.chat.id, s)


@bot.message_handler(func=lambda mess: mess.text == 'Пары на завтра')
def send_today(message):
    group_id = bk.output(message.chat.id)
    s = 'Пар нет'
    i = 1
    while s == 'Пар нет':
        start_time = datetime.datetime.today() + datetime.timedelta(days=i)
        start_time = start_time.strftime("%Y.%m.%d")
        s = bk.get_schedule(str(group_id), start_time, start_time)
        i += 1
    bot.send_message(message.chat.id, s)


@bot.message_handler(func=lambda mess: mess.text == 'Пары на каждый день недели')
def week(message):
    bot.send_message(message.chat.id, 'Выбери день недели', reply_markup=keyboard_week)


@bot.message_handler(func=lambda mess: mess.text in dn)
def week_day(message):
    group_id = bk.output(message.chat.id)
    start_time = mt.get_prev_date(dn[message.text]).strftime("%Y.%m.%d")
    s = bk.get_schedule(str(group_id), start_time, start_time)
    bot.send_message(message.chat.id, s)


@bot.message_handler(func=lambda mess: mess.text == 'Какая идет неделя?')
def week(message):
    if int(mt.week_number()) % 2 == 0:
        s = 'Четная'
    else:
        s = 'Нечетная'
    bot.send_message(message.chat.id, s)


@bot.message_handler(func=lambda mess: mess.text == 'Главное меню')
def menu_ret(message):
    bot.send_message(message.chat.id, 'Возвращаемся в главное меню', reply_markup=keyboard_func)


@bot.message_handler(func=lambda mess: mess.text == 'Календарь')
def start(m):
    calendar, step = DetailedTelegramCalendar(locale='ru', calendar_id=1).build()
    bot.send_message(m.chat.id,
                     f"Выберите начало периода",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(c):
    result, key, step = DetailedTelegramCalendar(locale='ru', calendar_id=1).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите начало периода",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Начало периода: {result}",
                              c.message.chat.id,
                              c.message.message_id)
        global start_date
        start_date = result.strftime("%Y.%m.%d")
        calendar, step = DetailedTelegramCalendar(locale='ru', calendar_id=2).build()
        bot.send_message(c.message.chat.id,
                         f"Выберите конец периода",
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal(c):
    result, key, step = DetailedTelegramCalendar(locale='ru', calendar_id=2).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите конец периода",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Конец периода: {result}",
                              c.message.chat.id,
                              c.message.message_id)
        finish_date = result.strftime("%Y.%m.%d")
        group_id = bk.output(c.message.chat.id)
        global start_date
        s = bk.get_schedule(str(group_id), start_date, finish_date)
        bot.send_message(c.message.chat.id, s)


@server.route('/' + '969496999:AAGEbpaVvifHffkjWHzKfvp8Kw-DUonja5U', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telebotik123.herokuapp.com/' + '969496999:AAGEbpaVvifHffkjWHzKfvp8Kw-DUonja5U')
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

