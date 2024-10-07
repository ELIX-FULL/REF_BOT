from telebot import types


# Кнопки со всеми продуктами(основное меню)
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Профиль👤", callback_data="profile"))
    markup.add(types.InlineKeyboardButton("Поддержка❓", callback_data='help'))
    markup.add(types.InlineKeyboardButton("Получить бонус🎁", callback_data='bonus'))
    return markup
