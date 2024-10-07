import os
import random
from datetime import timedelta

import telebot
from dotenv import load_dotenv
from telebot import types

import buttons
import database
from database import *

load_dotenv()
bot = telebot.TeleBot(token=os.getenv('TOKEN'), parse_mode='HTML', disable_web_page_preview=True)
name_bot = 'Название твоего бота'


@bot.message_handler(commands=['start'])
def start(message):
    """Приветствие в бот"""
    user_id = message.from_user.id
    if message.text.startswith('/start '):
        referrer = message.text.split(' ')[1]
        if int(referrer) == user_id:
            bot.send_message(user_id, f'<b>❕Самого себя рефералить нельзя</b>', reply_markup=buttons.main_menu())
        else:
            if check_user(user_id):
                bot.send_message(user_id, 'Главное меню', reply_markup=buttons.main_menu())
            else:
                new_user(referrer, user_id)
                bot.send_message(referrer, f'<b>У Вас новый реферал: @{message.from_user.username}</b>',
                                 reply_markup=buttons.main_menu())
                bot.send_message(user_id, 'Главное меню', reply_markup=buttons.main_menu())
                add_ref_balance(referrer)
    else:
        if check_user(user_id):
            bot.send_message(user_id, 'Главное меню', reply_markup=buttons.main_menu())
        else:
            new_user(0, user_id)
            bot.send_message(user_id, 'Главное меню', reply_markup=buttons.main_menu())


@bot.callback_query_handler(func=lambda call: call.data in ['help', 'profile', 'bonus'])
def call_handler(call):
    """ПОЛУЧЕНИЕ ПРОФИЛЯ ПОМОЩИ БОНУСА"""
    user_id = call.message.chat.id

    if call.data == 'profile':
        bot.answer_callback_query(call.id)

        if check_user(user_id):
            balance, refs = get_info(user_id)
            if balance is not None and refs is not None:
                markup = types.InlineKeyboardMarkup()
                invite_link = types.InlineKeyboardButton(text='🔗Ссылка для приглашения',
                                                         switch_inline_query=f'https://t.me/{name_bot}?start={user_id}')
                markup.add(invite_link)

                bot.send_message(
                    user_id,
                    f'<b>👤Профиль</b>\n\n' +
                    f'<i>👥Ты привел: {refs} друзей\n' +
                    f'💰Баланс: {balance} NOT\n\n</i>' +
                    f'Ссылка для приглашения: https://t.me/{name_bot}?start={user_id}',
                    reply_markup=markup
                )
            else:
                bot.send_message(user_id, "Ошибка при получении информации о пользователе.")
        else:
            new_user(0, user_id)  # Register user if not found
            bot.send_message(user_id, 'Главное меню', reply_markup=buttons.main_menu())

    elif call.data == 'help':
        bot.answer_callback_query(call.id)
        bot.send_message(
            user_id,
            '<a href="https://t.me/UZ_ELEGANT"><b>Поддержка❓</b></a>',
            reply_markup=buttons.main_menu()
        )
    elif call.data == 'bonus':
        bot.answer_callback_query(call.id)

        if bonusAccess(user_id):  # Проверяем, может ли пользователь получить бонус
            bonus = random.randint(1, 100)
            if database.add_bonus(bonus, user_id):
                bot.send_sticker(user_id, 'CAACAgIAAxkBAAEM7lBnBAjssgQeD689YI39d4jlkhWIPQACiA0AArvroUsJnEE_AtcneDYE')
                bot.send_message(user_id, f'<b>🎁 Вы получили бонус: {bonus} РУБ!</b>')
            else:
                bot.send_message(user_id, '<b>Ошибка получения бонуса.</b>')
        else:
            # Получаем время до следующего бонуса
            with sqlite3.connect('people.db') as db:
                cursor = db.cursor()
                last_bonus = \
                    cursor.execute('SELECT last_bonus_date FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]
                last_bonus_date = datetime.strptime(last_bonus, "%Y-%m-%d %H:%M:%S")
                next_bonus_date = last_bonus_date + timedelta(hours=72)  # 72 - 3 дня | 24 - 1 день
                time_left = next_bonus_date - datetime.now()

            hours, remainder = divmod(time_left.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            bot.send_message(user_id,
                             f'<b>Вы уже получили бонус. Следующий будет доступен через {int(hours)} часов и {int(minutes)} минут.</b>')


if __name__ == '__main__':
    bot.infinity_polling()
