from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup
import sqlite3
import time
import requests
import random
from settings import TOKEN


def start(update, context):
    '''Стартовый диалог'''
    reply_keyboard = [['/start', '/put_event'],
                      ['/print_events', '/every_morning'],
                      ['/random_picture', '/help']]  # кнопки клавиатуры
    # подключение клавиатуры
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    # приветственное сообщение
    update.message.reply_text('''Привет! ✋
Перед началом работы необходимо ответить на несколько вопросов''')
    update.message.reply_text(
                              "Как вас зовут?",
                              reply_markup=markup
                            )  # сообщение первого вопроса
    return 1


def first_response(update, context):
    '''Первый вопрос'''
    context.user_data['name'] = update.message.text  # запись с сообщения
    con = sqlite3.connect('events.db')  # подключение базы данных
    cur = con.cursor()
    # считывание имени с базы данных
    result = cur.execute(f'''SELECT inform FROM name_and_animal
                            WHERE id = "1"''').fetchall()
    if len(result) == 0:  # если пользователь не вводил имя до этого
        # добавить имя
        cur.execute(f'''INSERT INTO name_and_animal
                        VALUES ('1',
                                '{context.user_data['name']}')''')
    else:  # если пользователь вводил имя до этого
        # изменение имени
        cur.execute(f'''UPDATE name_and_animal
SET inform = "{context.user_data['name']}" WHERE id = "1"''')
    con.commit()  # сохранение
    con.close()  # закрытие базы данных
    update.message.reply_text(f"""Хорошо, {context.user_data['name']}!
А кого вы больше любите: кошек или собак?
Варианты ответа: кошек, собак""")  # сообщение второго вопроса
    return 2


def second_response(update, context):
    try:
        # клавиши клавиатуры
        reply_keyboard = [['/start', '/put_event'],
                          ['/print_events', '/every_morning'],
                          ['/random_picture', '/help']]
        # подключение клавиатуры
        markup = ReplyKeyboardMarkup(reply_keyboard,
                                     one_time_keyboard=False)
        # считывание текста сообщения
        context.user_data['cat_or_dog'] = update.message.text.lower()
        if 'кошек' not in context.user_data['cat_or_dog'] \
           and 'собак' not in context.user_data['cat_or_dog']:
            # если пользователь ввел не по правилам, вызвать ошибку
            raise Exception
        con = sqlite3.connect('events.db')  # подключение базы данных
        cur = con.cursor()
        # считывание предпочтения в животном с базы данных
        result = cur.execute(f'''SELECT inform FROM name_and_animal
WHERE id = "2"''').fetchall()
        if len(result) == 0:  # если пользователь не вводил до этого
            # добавление предпочтения
            cur.execute(f'''INSERT INTO name_and_animal
VALUES ('2', '{context.user_data['cat_or_dog']}')''')
        else:  # если пользователь вводил до этого
            # изменение предпочтения
            cur.execute(f'''UPDATE name_and_animal
SET inform = "{context.user_data['cat_or_dog']}" WHERE id = "2"''')
        con.commit()  # сохранение
        con.close()  # закрытие базы данных
        # вывод сообщения с информацией о командах
        update.message.reply_text('''Отлично! Теперь мы можем начать работу! ✅
Если вы хотите добавить новое дело в список - "/put_event" 📝
Если вы хотите посмотреть список на определенный день -
"/print_events" 👀
Если вы хотите, чтобы список дел был вам прислан
в определенное время -
"/every_morning" ⏰
Если вы хотите получить случайную картинку для
поднятия настроения -
"/random_picture" 🌅
Если вы хотите изменить имя или предпочтение по животному -
"/start" 🐱🐶''',
                                  reply_markup=markup
                                  )
        return ConversationHandler.END
    except Exception:  # если была вызвана ошибка
        # вывод сообщения об ошибке
        update.message.reply_text('''❗ Ой, что-то пошло не так!
Проверьте правильность введения данных и попробуйте ещё раз ❗''')
        return ConversationHandler.END


def stop(update, context):
    return ConversationHandler.END


def put_events(update, context):
    '''добавление дела'''
    # вывод сообщения
    update.message.reply_text(f"""Чтобы добавить дело в список,
напишите его в формате
<день в формате DD/MM/YYYY> <время в формате HH:MM> <дело>""")
    return 1


def update_to_db(update, context):
    try:
        # кнопки клавиатуры
        reply_keyboard = [['/start', '/put_event'],
                          ['/print_events', '/every_morning'],
                          ['/random_picture', '/help']]
        # добавление клавиатуры
        markup = ReplyKeyboardMarkup(reply_keyboard,
                                     one_time_keyboard=False)
        text = update.message.text  # считывание текста сообщения
        # преобразование данных в нужных формат
        text = text.split()
        event = ' '.join(text[2:])  # дело
        time = text[1]  # время
        day = text[0]  # дата
        if ':' not in time:  # если в неверном формате
            raise Exception
        if '/' not in day:  # если в неверном формате
            raise Exception
        con = sqlite3.connect('events.db')  # подключение базы данных
        cur = con.cursor()
        # добавление дела в базу данных
        cur.execute(f'''INSERT INTO days_and_events
VALUES ('{day}', '{time}', '{event}')''')
        con.commit()  # сохранение
        con.close()  # закрытие базы данных
        update.message.reply_text(
                                "Отлично! Дело добавлено! ✅",
                                reply_markup=markup
                                )  # вывод сообщения об успешном добавлении
        return ConversationHandler.END
    except Exception:  # если произошла ошибка
        # вывод сообщения об ошибке
        update.message.reply_text('''❗ Ой, что-то пошло не так!
Проверьте правильность введения данных и попробуйте ещё раз ❗''')
        return ConversationHandler.END


def print_events(update, context):
    '''какой день нужно вывести'''
    update.message.reply_text(f'''Список дел какого дня вы хотите узнать?
Напишите ответ в формате <DD/MM/YYYY>''')  # сообщение с вопросом
    return 1


def print_into_db(update, context):
    '''вывод списка дел'''
    try:
        # кнопки клавиатуры
        reply_keyboard = [['/start', '/put_event'],
                          ['/print_events', '/every_morning'],
                          ['/random_picture', '/help']]
        # вывод клавиатуры
        markup = ReplyKeyboardMarkup(reply_keyboard,
                                     one_time_keyboard=False)
        day_for_print = update.message.text  # считывание даты с сообщения
        if '/' not in day_for_print:  # если неверный формат
            raise Exception
        con = sqlite3.connect('events.db')  # подключение базы данных
        cur = con.cursor()
        # считывание дел на день
        result = cur.execute(f'''SELECT * FROM days_and_events
                                  WHERE day = "{day_for_print}"''')
        text = [f'Список дел на {day_for_print} ✏ \n']
        pod = []
        for elem in result:  # добавление к объекту для вывода дел
            pod.append(f"{elem[1]} - {' '.join(elem[2:])}\n")
        # сортировка по времени
        pod = sorted(pod, key=lambda x: int(x.split(':')[0]))
        text.extend(pod)  # добавление к основному массиву для вывода
        update.message.reply_text(
                                ' '.join(text),
                                reply_markup=markup
                                )  # вывод списка
        con.commit()  # сохранение
        con.close()  # закрытие базы данных
        return ConversationHandler.END
    except Exception:  # в случае ошибки
        # вывод сообщения
        update.message.reply_text('''❗ Ой, что-то пошло не так!
Проверьте правильность введения данных и попробуйте ещё раз ❗''')
        return ConversationHandler.END


def every_morning(update, context):
    '''считывание времени, в которое необходимо прислать'''
    update.message.reply_text('''Во сколько вам прислать план на день?
Напишите ответ в формате <HH:MM>''')
    return 1


def print_for_morning(update, context):
    try:
        # кнопки клавиатуры
        reply_keyboard = [['/start', '/put_event'],
                          ['/print_events', '/every_morning'],
                          ['/random_picture', '/help']]
        # добавление клавиатуры
        markup = ReplyKeyboardMarkup(reply_keyboard,
                                     one_time_keyboard=False)
        # добавление api
        cat_request = 'https://api.thecatapi.com/v1/images/search'
        dog_request = 'https://dog.ceo/api/breeds/image/random'
        # словарь с месяцами в формате time
        dct = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
               'May': '05', 'June': '06', 'July': '07', 'Aug': '08',
               'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        # время сейчас
        time_for_check = time.asctime().split()[3]
        time_right = update.message.text  # время для вывода
        if ':' not in time_right:  # если в неверном формате
            raise Exception  # вызов ошибки
        time_for_check = time_for_check.split(':')  # в нужный формат
        update.message.reply_text(
                                'Хорошо, ожидайте ⏰',
                                reply_markup=markup
                                )  # сообщение об успешной постановки задачи
        # если время не настало
        while ':'.join(time_for_check[:-1]) != time_right:
            time_for_check = time.asctime().split()[3]  # время сейчас
            time_for_check = time_for_check.split(':')  # в нужный формат
        date_for_check = []  # массив для даты
        date_now = time.asctime().split()[1:3]  # дата сейчас
        date_for_check.append(date_now[1])  # добавление дня
        date_for_check.append(dct[date_now[0]])  # добавление месяца
        year = time.asctime().split()[-1]  # добавление года
        date_for_check.append(year)  # добавление в главный массив для даты
        # преобразование в нужный формат
        date_for_check = '/'.join(date_for_check)
        con = sqlite3.connect('events.db')  # подключение базы данных
        cur = con.cursor()
        # считывание дел на день
        result = cur.execute(f'''SELECT * FROM days_and_events
                                  WHERE day =
                                  "{date_for_check}"''').fetchall()
        # считывание имени
        name_sql = cur.execute(f'''SELECT inform FROM name_and_animal
                            WHERE id = "1"''').fetchall()
        if len(name_sql) == 0:  # если пользователь не вводил имя
            raise Exception  # вызов ошибки
        for elem in name_sql:
            name = elem[0]  # запись имени
        # считывание предпочтения животного
        animal_sql = cur.execute(f'''SELECT inform FROM name_and_animal
                                     WHERE id = "2"''').fetchall()
        if len(animal_sql) == 0:  # если пользователь не выбирал животное
            raise Exception  # вызов ошибки
        for elem in animal_sql:
            animal = elem[0]  # запись животного
        text = [f'Привет, {name}! ✋ \n']  # приветственное сообщение
        # добавление текста
        text.append(f'Список дел на {date_for_check} ✏ \n')
        pod = []
        for elem in result:
            # добавление дела с список
            pod.append(f"{elem[1]} - {' '.join(elem[2:])}\n")
        # сортировка по времени
        pod = sorted(pod, key=lambda x: int(x.split(':')[0]))
        text.extend(pod)  # добавление в основной массив
        update.message.reply_text(' '.join(text))  # вывод сообщения
        if animal.lower() == 'кошек':  # если пользователь выбирал кошек
            responce = requests.get(cat_request)  # подключение api
            json_responce = responce.json()  # преобразование в json
            toponym = json_responce[0]['url']  # url на изображение
        elif animal.lower() == 'собак':  # если пользователь выбирал собак
            responce = requests.get(dog_request)  # подключение api
            json_responce = responce.json()  # преобразование в json
            toponym = json_responce['message']  # url на изображение
        update.message.reply_text(toponym)  # вывод изображения
        con.commit()  # сохранение
        con.close()  # закрытие базы данных
        return ConversationHandler.END
    except Exception:  # если была вызвана ошибка
        if len(name_sql) == 0:  # если пользователь не ввел имя
            update.message.reply_text('''❗ Вы не ввели своё имя!
Введите команду "/start" для введения имени ❗''')
        elif len(animal_sql) == 0:  # если пользователь не выбрал животного
            update.message.reply_text('''❗ Вы не выбрали животного,
который вам нравится! Введите команду "/start" для введения животного ❗''')
        else:  # в остальных случаях
            update.message.reply_text('''❗ Ой, что-то пошло не так!
Проверьте правильность введения данных и попробуйте ещё раз ❗''')
        return ConversationHandler.END


def random_picture(update, context):
    '''вывод случайной картинки'''
    try:
        con = sqlite3.connect('events.db')  # подключение базы данных
        cur = con.cursor()
        # считывание имени пользователя
        name_sql = cur.execute(f'''SELECT inform FROM name_and_animal
                            WHERE id = "1"''').fetchall()
        if len(name_sql) == 0:  # если пользователь не ввел имя
            raise Exception  # вызов ошибки
        for elem in name_sql:
            name = elem[0]  # добавление имени
        # вывод сообщения
        update.message.reply_text(f"Специально для вас, {name}! ✨")
        # добавление id доступных картинок
        ids = [0, 1]
        ids.extend([i for i in range(1000, 1084)])
        ids.extend([j for j in range(100, 148)])
        ids.extend([w for w in range(149, 180)])
        ids.extend([q for q in range(10, 18)])
        rand_number = random.choice(ids)  # случайный выбор одной из картинок
        # подключение api
        request = f'https://picsum.photos/id/{rand_number}/300'
        # кнопки клавиатуры
        reply_keyboard = [['/start', '/put_event'],
                          ['/print_events', '/every_morning'],
                          ['/random_picture', '/help']]
        # подключение клавиатуры
        markup = ReplyKeyboardMarkup(reply_keyboard,
                                     one_time_keyboard=False)
        # вывод изображения
        update.message.reply_text(request, reply_markup=markup)
    except Exception:  # если вызвана ошибка
        if len(name_sql) == 0:  # если пользователь не ввел имя
            update.message.reply_text('''❗ Кажется, вы забыли ввести имя.
Вызовите команду "/start", чтобы ввести имя ❗''')
        else:  # другие ошибки
            update.message.reply_text('''❗ Ой, что-то пошло не так!
Проверьте правильность введения данных и попробуйте ещё раз ❗''')
        return ConversationHandler.END


def help_(update, context):
    '''информация о командах'''
    # кнопки клавиатуры
    reply_keyboard = [['/start', '/put_event'],
                      ['/print_events', '/every_morning'],
                      ['/random_picture', '/help']]
    # подключение клавиатуры
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    # вывод сообщения
    update.message.reply_text('''
Если вы хотите добавить новое дело в список - "/put_event" 📝
Если вы хотите посмотреть список на определенный день -
"/print_events" 👀
Если вы хотите, чтобы список дел был вам прислан
в определенное время -
"/every_morning" ⏰
Если вы хотите получить случайную картинку для
поднятия настроения -
"/random_picture" 🌅
Если вы хотите изменить имя или предпочтение по животному -
"/start" 🐱🐶''', reply_markup=markup)


def main():
    '''основная функция'''
    # подключение
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    # стартовый диалог
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(Filters.text, first_response)],
            2: [MessageHandler(Filters.text, second_response)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)  # подключение команд
    # диалог добавления дела
    make_for_put = ConversationHandler(
        entry_points=[CommandHandler('put_event', put_events)],
        states={
            1: [MessageHandler(Filters.text, update_to_db)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(make_for_put)  # подключение команд
    # диалог вывода списка дел
    print_events_for_day = ConversationHandler(
        entry_points=[CommandHandler('print_events', print_events)],
        states={
            1: [MessageHandler(Filters.text, print_into_db)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(print_events_for_day)  # подключение команд
    # диалог вывода списка дел в определенное время
    print_to_morning = ConversationHandler(
        entry_points=[CommandHandler('every_morning', every_morning)],
        states={
            1: [MessageHandler(Filters.text, print_for_morning)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(print_to_morning)  # подключение команд
    # подключение команды случайной картинки
    dp.add_handler(CommandHandler('random_picture', random_picture))
    # подключение команды помощи
    dp.add_handler(CommandHandler('help', help_))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()  # вызов основной функции
