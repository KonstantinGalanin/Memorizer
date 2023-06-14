import telebot
from telebot import types

import threading
import time


bot = telebot.TeleBot('6044842339:AAF9k33I5WndApAAK3IECOv5W9RaWTg6B3o') 
# bot = telebot.TeleBot('6012219357:AAFNgGBDuCkPe7kLdd8VH9pMUUH-xr2N9jY') #тестовый

theme_dict = {}
flags_dict = {}

INT_1 = 900
INT_2 = 7200
INT_3 = 86400
INT_4 = 259200
INT_5 = 604800
INT_6 = 1209600
INT_7 = 2505600
time_markers = (INT_1,INT_2,INT_3,INT_4,INT_5,INT_6,INT_7,0)#15м, 2ч, 1д, 3д, 1н, 2н, 1мес


#Создает меню при старте бота и занесение в словарь информации
def create_menu(message, app):
    if app == 'start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Запомнить")
        item2 = types.KeyboardButton("Посмотреть имеющиеся темы")
        markup.add(item1,item2)
        bot.send_message(message.from_user.id, 'Если хочешь что то запомнить нажми на кнопку "Запомнить" и кратко опиши тему того, что ты хочешь запомнить', 
        disable_notification=True,
        reply_markup = markup)

        user_reg(message)

#Внесение информации о пользователе в словарь
def user_reg(message):
    user = str(message.chat.id)
    theme_dict[user] = {}

    flags_dict[user] = {}
    flags_dict[user]['remember_btn'] = False
    flags_dict[user]['word_to_del'] = False
    flags_dict[user]['descript_to_show'] = False
    flags_dict[user]['examined_themes'] = []
    flags_dict[user]['message'] = message


# Удаляет по запросу любую тему
def delete_theme(theme,user):
    if theme in flags_dict[user]['examined_themes']:
        flags_dict[user]['examined_themes'].remove(theme)
        bot.send_message(user, "Тема удалена",disable_notification=True)
    elif theme in theme_dict[user].keys():
        del theme_dict[user][theme] 
        bot.send_message(user, "Тема удалена",disable_notification=True)
    else:
        bot.send_message(user, "Такой темы нет",disable_notification=True) # 162 строчка

# Показывает описание к теме
def show_description(theme,user):
    if theme in flags_dict[user]['examined_themes']:
        descript = flags_dict[user]['examined_themes'][theme]
        bot.send_message(user, f'Определение к теме {theme}:\n"{descript}"',disable_notification=True)
    elif theme in theme_dict[user]:
        descript = theme_dict[user][theme]['description']
        bot.send_message(user, f'Определение к теме {theme}:\n"{descript}"',disable_notification=True)
    else:
        bot.send_message(user, "Такой темы нет",disable_notification=True) # 162 строчка

# создает кнопки в сообщении просмотра тем
def create_btn_watch(user):
    # word_to_del = flags_dict[user]['word_to_del']
    markup_del = types.InlineKeyboardMarkup() #new
    item_del = types.InlineKeyboardButton("Удалить тему",callback_data='delete_btn')
    item_description = types.InlineKeyboardButton("Определения",callback_data='description_btn')
    markup_del.add(item_del,item_description)
    bot.send_message(user, all_themes(user),disable_notification=True, reply_markup= markup_del)

# записывает все темы и время до повтора
def all_themes(user):
    if theme_dict:
        current_themes = [theme for theme in theme_dict[user]]
        current_times = get_time(user)
        current_pairs = list(zip(current_themes,current_times))
        current = "Нынешние темы:\n" + '\n'.join(["· "+' '.join(map(str, pair)) for pair in current_pairs])
    else:
        current = "Нынешние темы:\n"
    examined = "\n\nИзученные темы:\n"+"\n".join(["· " + exam for exam in flags_dict[user]['examined_themes']])
    return current + examined

# получает оставшееся время до повтора для каждой темы 
def get_time(user):
    current_times = []
    for message_text,values in theme_dict[user].items():
        index = theme_dict[user][message_text]['index']
        btn_pressed = theme_dict[user][message_text]['btn_pressed']
        if btn_pressed == True:
            duration = format_time(time_markers[index] - (time.time() - values['start']))
        else:
            duration = '-'
        current_times.append(duration)
    return current_times

# переводит время из секунд в минуты, часы или дни
def format_time(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    time_string = ""
    if days > 0:
        time_string += f"{days}д "
    if hours > 0: # Исправил
        time_string += f"{hours}ч"
    elif minutes > 0:
        time_string += f"{minutes}м"
    else:
        time_string += f"{int(seconds)}cек"
    return ": " + time_string

# Мониторит старт бота и запускает ф-ию
@bot.message_handler(commands=["start"])
def start(message):
    create_menu(message,'start')

# Мониторит ввод новых тем или нажатие кнопок в меню
@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):
    user = str(message.chat.id)
    if user not in flags_dict: # временно изменено
        bot.send_message(user, 'Нажмите на /start',disable_notification=True)
        return 0 #сделать через create_menu
        # create_menu(message,'start')
    message_text = message.text
    remember_btn = flags_dict[user]['remember_btn']
    word_to_del = flags_dict[user]['word_to_del']
    descript_to_show = flags_dict[user]['descript_to_show']
    examined_themes = flags_dict[user]['examined_themes']
    if message_text == "Запомнить":
        bot.send_message(user, "Введите тему:",disable_notification=True)
        remember_btn = True
    elif remember_btn == True:
        remember_btn = False
        if message_text in theme_dict[user] or message_text in examined_themes: 
            bot.send_message(user, "Эта тема уже есть",disable_notification=True)
        else:
            theme_dict[user][message_text] = {}
            theme_dict[user][message_text]['start'] = int(time.time())
            theme_dict[user][message_text]['index'] = -1
            theme_dict[user][message_text]['btn_pressed'] = True
            theme_dict[user][message_text]['description'] = ''
            bot.send_message(message.from_user.id, f"Напишите определение к теме {message_text}",disable_notification=True)

    elif message_text == "Посмотреть имеющиеся темы":
        create_btn_watch(user)

    # elif (message_text in theme_dict[user] or message_text in flags_dict[user]['examined_themes']) and word_to_del == True:
    elif word_to_del == True: #Ну хз
        word_to_del = False
        delete_theme(message_text,user)
    # elif (message_text in theme_dict[user] or message_text in flags_dict[user]['examined_themes']) and descript_to_show == True:
    elif descript_to_show == True: #Ну хз
        descript_to_show = False
        show_description(message_text,user)
    else:
        for theme in theme_dict[user]:
            if theme_dict[user][theme]['description'] == '':
                theme_dict[user][theme]['description'] = message_text

    
    flags_dict[user]['remember_btn'] = remember_btn
    flags_dict[user]['word_to_del'] = word_to_del
    flags_dict[user]['descript_to_show'] = descript_to_show

# Мониторит нажатие кнопок в сообщениях и выполняет соответствуюющие задачи
@bot.callback_query_handler(func = lambda call: True)
def answer(call):
    user = str(call.message.chat.id)
    if call.data in ['yes_i_remember','no_i_didnt_remember']:
        string = str(call.message.text)
        message_text = string[string.find(' ')+1:string.find('?')]
        index = theme_dict[user][message_text]['index']
        description = theme_dict[user][message_text]['description']
        if call.data == 'yes_i_remember':
            if time_markers[index] != 0:
                bot.send_message(user, f'Отлично, повторим тему {message_text} через {format_time(time_markers[index])[2:]}',
                disable_notification=True)
            else:
                bot.send_message(user, 'Поздравляю вы выучили тему !!!', disable_notification=True)
                flags_dict[user]['examined_themes'].append({message_text:description})
                theme_dict[user].pop(message_text, None)

        if call.data == 'no_i_didnt_remember':
            if index in [0,1]:
                index -= 1
                theme_dict[user][message_text]['index'] = index
            else:
                index -= 2
                theme_dict[user][message_text]['index'] = index
            bot.send_message(user, f'Жаль(\nОпределение темы {message_text}:\n"{description}"\nПовторим тему через {format_time(time_markers[index])[2:]}',
            disable_notification=True)
    
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        theme_dict[user][message_text]['start'] = int(time.time())
        theme_dict[user][message_text]['btn_pressed'] = True

    if call.data == 'delete_btn':
        if theme_dict:
            bot.send_message(user, 'Введите тему, которую хотите удалить',disable_notification=True)
            flags_dict[user]['word_to_del'] = True
        else:
            bot.send_message(user, 'Тем для удаления нет',disable_notification=True)
    if call.data == 'description_btn':
        if theme_dict:
            bot.send_message(user, 'Введите тему, у которой хотите посмотреть определение',disable_notification=True)
            flags_dict[user]['descript_to_show'] = True
        else:
            bot.send_message(user, 'Тем для просмотра описания нет',disable_notification=True)


# Первая часть закончена

#Мониторит когда следует отправить вопрос пользователю о том, запомнил ли он тему
def chk_theme():
    for user in list(theme_dict):
        for message_text in theme_dict[user]:
            index = theme_dict[user][message_text]['index']
            start = theme_dict[user][message_text]['start']
            btn_pressed = theme_dict[user][message_text]['btn_pressed']
            
            if time.time() - time_markers[index] >= start and btn_pressed == True and theme_dict[user][message_text]['description'] != '':
                if index < len(time_markers)-1:
                    create_btn_check(flags_dict[user]['message'],message_text)
                    theme_dict[user][message_text]['start'] = int(time.time())
                    theme_dict[user][message_text]['index'] = index+1
                    theme_dict[user][message_text]['btn_pressed'] = False


def create_btn_check(message,message_text):
    markup = types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton("Да",callback_data='yes_i_remember')
    item_no = types.InlineKeyboardButton("Нет",callback_data='no_i_didnt_remember')
    markup.add(item_yes,item_no)

    bot.send_message(message.chat.id, f'Запомнили {message_text}?',
    disable_notification=True,
    reply_markup= markup)

# Вторая часть закончена

def run_receive_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except telebot.apihelper.ApiException as e:
            # Ошибка 502 может быть вызвана проблемами с сервером Telegram
            # Добавьте логику повторной попытки подключения через некоторое время
            print(f"Ошибка 502: {e}")
            time.sleep(5) 

def run_send_bot():
    try:
        chk_theme()
        time.sleep(3)
    except Exception as e:

        # print("-------run_send_bot------\n")
        print(e)
        # print('Была ошибка')


bot_thread = threading.Thread(target=run_receive_bot)
bot_thread.start()

while True:
    run_send_bot()