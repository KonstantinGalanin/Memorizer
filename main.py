import telebot
import threading
import time
from storage import DataBase
import buttons
import time_utils


bot = telebot.TeleBot('<KEY>') 

INT_1 = 15 * 60
INT_2 = 2 * 60 * 60
INT_3 = 24 * 60 * 60
INT_4 = 3 * 24 * 60 * 60
INT_5 = 7 * 24 * 60 * 60
INT_6 = 2 * 7 * 24 * 60 * 60
INT_7 = 4 * 7 * 24 * 60 * 60
time_markers = (INT_1,INT_2,INT_3,INT_4,INT_5,INT_6,INT_7,0)#15м, 2ч, 1д, 3д, 1н, 2н, 1мес
database = DataBase()

# Мониторит старт бота
@bot.message_handler(commands=["start"])
def start(message):
    buttons.create_menu(bot,database,message)

# Мониторит ввод новых тем или нажатие кнопок в меню
@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):
    user = str(message.chat.id)
    message_text = message.text
    remember_btn = database.read_inf(user,'remember_btn')
    word_to_del = database.read_inf(user,'word_to_del')
    descript_to_show = database.read_inf(user,'descript_to_show')
    if message_text == "Запомнить":
        bot.send_message(user, "Введите тему:",disable_notification=True)
        remember_btn = True
    elif remember_btn:
        remember_btn = False
        start = int(time.time())
        if database.theme_reg(message,start):
            bot.send_message(user, "Эта тема уже есть",disable_notification=True)
        else:
            bot.send_message(message.from_user.id, f"Напишите определение к теме {message_text}",disable_notification=True)

    elif message_text == "Посмотреть имеющиеся темы":
        all_themes(user)

    elif word_to_del:
        word_to_del = False
        delete_theme(message_text,user)
    elif descript_to_show:
        descript_to_show = False
        show_description(message_text,user)
    else:
        for theme in database.read_inf(user,'themes'):
            if database.read_inf(user,'description',theme) == '':
                database.edit_inf(user,'description',message_text,theme)
    
    database.edit_inf(user,'remember_btn',remember_btn)
    database.edit_inf(user,'word_to_del',remember_btn)
    database.edit_inf(user,'descript_to_show',remember_btn)


# Мониторит нажатие кнопок в сообщениях и выполняет соответствуюющие задачи
@bot.callback_query_handler(func = lambda call: True)
def answer(call):
    user = str(call.message.chat.id)
    if call.data in ['yes_i_remember','no_i_didnt_remember']:
        string = str(call.message.text)
        message_text = string[string.find(' ')+1:string.find('?')]
        index = database.read_inf(user,'index',message_text)
        description = database.read_inf(user,'description',message_text)
        if call.data == 'yes_i_remember':
            if time_markers[index] != 0:
                bot.send_message(user, f'Отлично, повторим тему {message_text} через {time_utils.format_time(time_markers[index])[2:]}',
                disable_notification=True)
            else:
                bot.send_message(user, 'Поздравляю вы выучили тему !!!', disable_notification=True)
                database.edit_inf(user,'add_to_examined',message_text)
                database.edit_inf(user,'delete_current',message_text)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                return 0

        if call.data == 'no_i_didnt_remember':
            if index in [0,1]:
                index -= 1
                database.edit_inf(user,'index',index,message_text)
            else:
                index -= 2
                database.edit_inf(user,'index',index,message_text)
            bot.send_message(user, f'Жаль(\nОпределение темы {message_text}:\n"{description}"\nПовторим тему через {time_utils.format_time(time_markers[index])[2:]}',
            disable_notification=True)
    
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        database.edit_inf(user,'start',int(time.time()),message_text)
        database.edit_inf(user,'btn_pressed',True,message_text)

    if call.data == 'delete_btn':
        if database.collection_exist(user):
            bot.send_message(user, 'Введите тему, которую хотите удалить',disable_notification=True)
            database.edit_inf(user,'word_to_del',True)
        else:
            bot.send_message(user, 'Тем для удаления нет',disable_notification=True)
    if call.data == 'description_btn':
        if database.collection_exist(user): 
            bot.send_message(user, 'Введите тему, у которой хотите посмотреть определение',disable_notification=True)
            database.edit_inf(user,'descript_to_show',True)
        else:
            bot.send_message(user, 'Тем для просмотра описания нет',disable_notification=True)

# Удаляет по запросу любую тему
def delete_theme(theme,user):
    # bot.send_message("1573383068", 2)
    if theme in database.read_inf(user,'examined_themes'):
        database.edit_inf(user,'delete_examined',theme)
        bot.send_message(user, "Тема удалена",disable_notification=True)
    elif theme in database.read_inf(user,'themes'):
        database.edit_inf(user,'delete_current',theme)
        bot.send_message(user, "Тема удалена",disable_notification=True)
    else:
        bot.send_message(user, "Такой темы нет",disable_notification=True) # 162 строчка

# Показывает описание к теме
def show_description(theme,user):
    if theme in database.read_inf(user,'themes'):
        descript = database.read_inf(user,'description',theme)
        bot.send_message(user, f'Определение к теме {theme}:\n"{descript}"',disable_notification=True)
    else:
        bot.send_message(user, "Такой темы нет",disable_notification=True) # 162 строчка

# записывает все темы и время до повтора
def all_themes(user):
    current_themes = database.read_inf(user,'themes')
    if current_themes != []:
        current_times = time_utils.get_time(database,user)
        current_pairs = list(zip(current_themes,current_times))
        current = "Нынешние темы:\n" + '\n'.join(["· "+' '.join(map(str, pair)) for pair in current_pairs])
    else:
        current = "Нынешние темы:\n"
    examined = "\n\nИзученные темы:\n"+"\n".join(["· " + exam for exam in database.read_inf(user,'examined_themes')])

    buttons.create_btn_watch(bot,user,current + examined)


#Мониторит когда следует отправить вопрос пользователю о том, запомнил ли он тему
def chk_theme():
    for user in database.read_all_id():
        for message_text in database.read_inf(user,'themes'):
            index = database.read_inf(user,'index',message_text)
            start = database.read_inf(user,'start',message_text)
            btn_pressed = database.read_inf(user,'btn_pressed',message_text)
            description = database.read_inf(user,'description',message_text)
            if time.time() - time_markers[index] >= start and btn_pressed and description != '':
                if index < len(time_markers)-1:
                    buttons.create_btn_check(bot,user,message_text)
                    database.edit_inf(user,'start',int(time.time()),message_text)
                    database.edit_inf(user,'index',index+1,message_text)
                    database.edit_inf(user,'btn_pressed',False,message_text)


def run_receive_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5) 

def run_send_bot():
    while True:
        try:
            chk_theme()
        except Exception as e:
            print(e)
        finally:
            time.sleep(1)

if __name__ == "__main__":
    thread_receive = threading.Thread(target=run_receive_bot)
    thread_send = threading.Thread(target=run_send_bot)

    thread_receive.start()
    thread_send.start()

