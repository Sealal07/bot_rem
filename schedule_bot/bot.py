import asyncio
import calendar
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types.message import Message
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import (create_db, get_user_reminder, add_reminder,
                delete_reminder, get_all_reminders, set_user_timezone,
                get_user_timezone)
from keyboard import  (get_main_keyboard, get_month_keyboard,
                       get_day_keyboard, get_year_keyboard,
                       get_timezone_keyboard, get_time_keyboard, month_dict)

from config import  TOKEN
import pytz

bot = Bot(TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

TIMEZONE_CITIES = ['Москва (UTC+3)', 'Новосибирск (UTC+7)',
                   'Алматы (UTC+6)', 'Другой']

TIMEZONE_MAP = {
                'Москва (UTC+3)': 'Europe/Moscow',
                'Новосибирск (UTC+7)': 'Asia/Novosibirsk',
               'Алматы (UTC+6)': 'Asia/Almaty'
}

user_reminder = {} #для хранения в памяти для удаления

# FSM для хранения конечных состояний (для напоминаний)
class ReminderStates(StatesGroup):
    choose_month = State()
    choose_year = State()
    choose_day = State()
    choose_time = State()
    choose_text = State()


# FSM для настройки часового пояса
class Timezone(StatesGroup):
    choosing_custom_timezone = State()
    requesting_delete_reminder = State()


# фоновая задача проверки напоминания
async def check_r(bot):
    while True:
        try:
            all_reminders = await get_all_reminders()
            now_utc = datetime.now(pytz.utc)
            for r_id, user_id, r_text, r_date, r_time in all_reminders:
                timezone_name = await get_user_timezone(user_id)
                if not timezone_name:
                    continue
                try:
                    day, month_name, year = r_date.split()
                    month = month_dict[month_name]
                    hour, minute = r_time.split(':')
                    reminder_time = datetime(int(year),
                                             month, int(day),
                                             int(hour), int(minute))
                #     локализируем время в часовом поясе пользователя
                    user_tz = pytz.timezone(timezone_name)
                    localized_time = user_tz.localize(reminder_time)
                    utc_time = localized_time.astimezone(pytz.utc)
                    if now_utc >= utc_time:
                        await bot.send_message(user_id,
                                               f'Напоминание: {r_text}')
                        await delete_reminder(r_id)
                except Exception as e:
                   print(f'Ошибка обработки напоминания {r_id} '
                         f'для {user_id}: {e}')

        except Exception as e:
            print(f'Критическая ошибка в check_r: {e}')

        await asyncio.sleep(20)

@router.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    timezone_name = await get_user_timezone(user_id)
    if not timezone_name:
        await message.answer(
            text='Привет! Для корректной работы выберите ваш'
                 'город или введите часовой пояс',
            reply_markup=get_timezone_keyboard()
        )
    else:
        await  message.answer(
            text='Добро пожаловать! Чем могу помочь?',
            reply_markup=get_main_keyboard()
        )

@router.message(F.text.in_(TIMEZONE_CITIES))
async def set_timezone_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    city = message.text
    print(user_id, city)
    if city == 'Другой':
        await message.answer(
            text='Пожалуйста, введите ваш часовой пояс в формате '
                 '"Continent/City" (например: "Europe/Moscow")',
            reply_markup=ReplyKeyboardRemove()
        )
        await  state.set_state(Timezone.choosing_custom_timezone)
    else:
        timezone_name = TIMEZONE_MAP[city]
        print(timezone_name)
        await set_user_timezone(user_id, timezone_name)
        await message.answer(
            text=f'Часовой пояс установлен: {city}. '
                 f'Теперь вы можете создать напоминание!',
            reply_markup=get_main_keyboard()
        )
        await state.clear()
@router.message(Timezone.choosing_custom_timezone)
async def custom_timezone_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    timezone_name = message.text.strip()
    try:
        pytz.timezone(timezone_name)
        await set_user_timezone(user_id, timezone_name)
        await message.answer(
            text=f'Часовой пояс установлен: {timezone_name}. '
                 f'Теперь вы можете создать напоминание!',
            reply_markup=get_main_keyboard()
        )
        await state.clear()
    except pytz.exceptions.UnknownTimeZoneError:
        await message.answer(
            text=f'Неизвестный часовой пояс! Пожалуйста, '
                 f'попробуйте еще раз'
        )

@router.message(F.text == 'Создать напоминание')
async def create_reminder_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    timezone_name = await get_user_timezone(user_id)
    if not timezone_name:
        await message.answer(
            'Сначала установите ваш часовой пояс',
            reply_markup=ReplyKeyboardRemove()
        )
        return
    await message.answer('Выберите месяц: ',
                         reply_markup=get_month_keyboard())
    await state.set_state(ReminderStates.choose_month)

@router.message(ReminderStates.choose_month, F.text.in_(month_dict.keys()))
async def choose_month_handler(message: Message, state: FSMContext):
    await state.update_data(month=message.text)
    await message.answer('Выберите год:',
                         reply_markup=get_year_keyboard())
    await state.set_state(ReminderStates.choose_year)

@router.message(ReminderStates.choose_year, F.text.in_(['2025', '2026', '2027', '2028']))
async def choose_year_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    month = data['month']
    year = message.text

    await state.update_data(year=year)

    await message.answer(
        f'Вы выбрали {month} {year}. \nВыберите день: ',
        reply_markup=get_day_keyboard(month, year)
    )
    await state.set_state(ReminderStates.choose_day)

@router.message(ReminderStates.choose_day)
async def choose_day_handler(message: Message, state: FSMContext):
    day_str = message.text.strip()
    if not day_str.isdigit():
        data = await state.get_data()
        await message.answer(
            'Пожалуйста, введите число!',
            reply_markup=get_day_keyboard(data['month'], data['year'])
        )
        return
    day = int(day_str)
    data = await  state.get_data()
    month = data['month']
    year = int(data['year'])
    month_num = month_dict[month]
    try:
        days_in_month = calendar.monthrange(year, month_num)[1]
        if 1 <= day <= days_in_month:
            await state.update_data(day=day)
            await message.answer(
                f'Вы выбрали {day}-{month}-{year}.\nТеперь выберите'
                f'или введите время в формате в HH:MM',
                reply_markup=get_time_keyboard()
            )
            await state.set_state(ReminderStates.choose_time)
        else:
            await message.answer(
                f'Такого дня в этом  месяце не существует.'
                f'Выберите правильный день',
                reply_markup=get_day_keyboard(month, year)
            )
    except Exception:
        await message.answer('Произошла ошибка при проверке даты.'
                             'Попробуйте еще раз')
        await state.clear()


@router.message(ReminderStates.choose_time)
async def choose_time_handler(message: Message, state: FSMContext):
    time_str = message.text.strip()
    if not re.match(r'^\d{2}:\d{2}$', time_str):
        await message.answer('Введите правильный формат времени:'
                             'HH:MM, (например 14:56)',
                             reply_markup=get_time_keyboard())
        return
    await state.update_data(time=time_str)
    data = await state.get_data()
    await message.answer(
        f'Вы выбрали {time_str}. '
        f'Дата: {data['day']}-{data['month']}-{data['year']}.'
        f'\nВведите текст напоминания:',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ReminderStates.choose_text)

@router.message(ReminderStates.choose_text)
async def choose_text_handler(message: Message, state: FSMContext):
    r_text = message.text
    user_id = message.from_user.id

    data = await state.get_data()
    day = data['day']
    month = data['month']
    year = data['year']
    r_date = f'{day} {month} {year}'
    r_time = data['time']

    await add_reminder(user_id, r_text, r_date, r_time)

    await message.answer('Напоминание сохранено!',
                         reply_markup=get_main_keyboard())
    await state.clear()


@router.message(F.text == 'Мои напоминания')
async def show_reminder_handler(message: Message):
    user_id = message.from_user.id
    reminders = await get_user_reminder(user_id)

    if not reminders:
        await message.answer('У вас нет напоминаний',
                             reply_markup=get_main_keyboard())
        return

    response = 'Ваши напоминания: \n'
    user_reminder[user_id] = reminders

    for i, (db_id, text, date, time) in enumerate(reminders, start=1):
        response += f'{i}. {text} - {date} в {time} \n'
    await message.answer(response, reply_markup=get_main_keyboard())

@router.message(F.text == 'Удалить напоминание')
async def delete_text_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in user_reminder or not user_reminder[user_id]:
        await message.answer('Сначала запросите список напоминаний',
                             reply_markup=get_main_keyboard())
        return
    await message.answer('Введите напоминания, которе хотите удалить',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(Timezone.requesting_delete_reminder)

@router.message(Timezone.requesting_delete_reminder)
async def delete_rem_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        reminder_num = int(message.text)
        reminders = user_reminder[user_id]
        if 1 <= reminder_num <= len(reminders):
            real_id = reminders[reminder_num-1][0]
            await delete_reminder(real_id)
            await message.answer('напоминание удалено',
                                 reply_markup=get_main_keyboard())
            del user_reminder[user_id]
            await show_reminder_handler(message)
        else:
            await message.answer('некорректный номер')
    except ValueError:
        await message.answer('введите число')
    except KeyError:
        await message.answer('Сначала запросите список напоминаний',
                             reply_markup=get_main_keyboard())
        await state.clear()

    if not state.get_state():
        await state.clear()










# reminder_time = datetime(2025, 10, 29, 18, 59)
# user_tz = pytz.timezone('Europe/Moscow')
# print(user_tz)
# localized_time = user_tz.localize(reminder_time)
# print(localized_time)
# utc_time = localized_time.astimezone(pytz.utc)
# print(utc_time)

async def main():
    await create_db()
    print('база готова')
    asyncio.create_task(check_r(bot))
    print('фоновая задача запущена')

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('бот остановлен')