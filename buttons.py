import telebot
from telebot import types

import time_utils

#Создает меню при старте бота и занесение в словарь информации
def create_menu(bot,database,message):
    # bot.send_message("1573383068", 1)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Запомнить")
    item2 = types.KeyboardButton("Посмотреть имеющиеся темы")
    markup.add(item1,item2)
    bot.send_message(message.from_user.id, 'Если хочешь что то запомнить нажми на кнопку "Запомнить" и кратко опиши тему того, что ты хочешь запомнить', 
    disable_notification=True,
    reply_markup = markup)

    database.user_reg(message)


# создает кнопки в сообщении просмотра тем
def create_btn_watch(bot,user,themes):
    markup_del = types.InlineKeyboardMarkup()
    item_del = types.InlineKeyboardButton("Удалить тему",callback_data='delete_btn')
    item_description = types.InlineKeyboardButton("Определения",callback_data='description_btn')
    markup_del.add(item_del,item_description)
    bot.send_message(user,themes,disable_notification=True, reply_markup= markup_del)


def create_btn_check(bot,user,message_text):
    markup = types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton("Да",callback_data='yes_i_remember')
    item_no = types.InlineKeyboardButton("Нет",callback_data='no_i_didnt_remember')
    markup.add(item_yes,item_no)

    bot.send_message(user, f'Запомнили {message_text}?',
    disable_notification=True,
    reply_markup= markup)

# # записывает все темы и время до повтора
# def all_themes(database,user):
#     current_themes = database.read_inf(user,'themes')
#     if current_themes != []:
#         current_times = time_utils.get_time(database,user)
#         current_pairs = list(zip(current_themes,current_times))
#         current = "Нынешние темы:\n" + '\n'.join(["· "+' '.join(map(str, pair)) for pair in current_pairs])
#     else:
#         current = "Нынешние темы:\n"
#     examined = "\n\nИзученные темы:\n"+"\n".join(["· " + exam for exam in database.read_inf(user,'examined_themes')])
#     return current + examined