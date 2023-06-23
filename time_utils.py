import time

INT_1 = 15*60
INT_2 = 2*60*60
INT_3 = 86400
INT_4 = 259200
INT_5 = 604800
INT_6 = 1209600
INT_7 = 2505600
time_markers = (INT_1,INT_2,INT_3,INT_4,INT_5,INT_6,INT_7,0)#15м, 2ч, 1д, 3д, 1н, 2н, 1мес

# получает оставшееся время до повтора для каждой темы 
def get_time(database,user):
    current_times = []
    for message_text in database.read_inf(user,'themes'):
        index = database.read_inf(user,'index',message_text)
        btn_pressed = database.read_inf(user,'btn_pressed',message_text)
        if btn_pressed == True and index != -1:
            start = database.read_inf(user,'start',message_text)
            duration = format_time(time_markers[index] - (time.time() - start))
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
    elif hours > 0:
        time_string += f"{hours}ч"
    elif minutes > 0:
        time_string += f"{minutes}м"
    else:
        time_string += f"{int(seconds)}cек"
    return ": " + time_string