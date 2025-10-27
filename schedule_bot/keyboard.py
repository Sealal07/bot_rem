from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import calendar

# основная клавиатура
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text='Создать напоминание')],
        [KeyboardButton(text='Мои напоминания'),
         KeyboardButton(text='Удалить напоминание')]
    ]
    markup = ReplyKeyboardMarkup(keyboard=buttons,
                                 resize_keyboard=True)
    return markup

# клавиатура для выбора месяца
def get_month_keyboard():
    buttons = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май',
               'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
               'Ноябрь', 'Декабрь']

    keyboard_rows=[]
    for i in range(0, len(buttons), 4):
        row = [KeyboardButton(text=month) for month in
               buttons[i:i+4]]
        keyboard_rows.append(row)
    markup = ReplyKeyboardMarkup(keyboard=keyboard_rows,
                                 resize_keyboard=True)
    return markup

# клавиатура для выбора дня
def get_day_keyboard(month, year):
    month_dict = {'Январь': 1, 'Февраль': 2, 'Март': 3,
                  'Апрель': 4, 'Май': 5, 'Июнь': 6, 'Июль': 7,
                  'Август': 8, 'Сентябрь': 9, 'Октябрь': 10,
                  'Ноябрь': 11, 'Декабрь': 12}
    try:
        month_num = month_dict[month]
        year = int(year)
        # получаем кол-во дней в месяце
        days_in_month = calendar.monthrange(year, month_num)[1]
    except (KeyError, ValueError, IndexError):
        return  get_main_keyboard()
    days = [KeyboardButton(text=str(i)) for i in
            range(1, days_in_month+1)]
    keyboard_rows = []
    for i in range(0, len(days), 7):
        keyboard_rows.append(days[i:i+7])
    markup = ReplyKeyboardMarkup(keyboard=keyboard_rows,
                                 resize_keyboard=True)
    return markup

def get_year_keyboard():
    years = ['2025', '2026', '2027', '2028']
    buttons = [[KeyboardButton(text=year) for year in years]]
    markup = ReplyKeyboardMarkup(keyboard=buttons,
                                 resize_keyboard=True)
    return markup

def get_time_keyboard():
    times = ['00:00', '12:00', '20:00', '22:00']
    buttons = [[KeyboardButton(text=time) for time in times]]
    markup = ReplyKeyboardMarkup(keyboard=buttons,
                                 resize_keyboard=True)
    return markup

def get_timezone_keyboard():
    buttons = ['Москва (UTC+3)', 'Новосибирск (UTC+7)',
               'Алматы (UTC+6)', 'Другой']
    buttons = [[KeyboardButton(text=text) for text in buttons]]
    markup = ReplyKeyboardMarkup(keyboard=buttons,
                                 resize_keyboard=True)
    return markup