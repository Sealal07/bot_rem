import asyncio
import calendar
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types.message import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import (create_db, get_user_reminder, add_reminder,
                delete_reminder, get_all_reminders, set_user_timezone,
                get_user_timezone)
from keyboard import  (get_main_keyboard, get_month_keyboard,
                       get_day_keyboard, get_year_keyboard,
                       get_timezone_keyboard, get_time_keyboard)

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

# FSM для настройки часового пояса
class Timezone(StatesGroup):
    choosing_custom_timezone = State()
    #


@router.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    timezone_name = await get_user_timezone(user_id)
    if not timezone_name:
        await message.answer(
            text='Привет! Для корректной работы выберите ваш'
                 'город или введите часовой пояс',
            reply_markup=get_main_keyboard()
        )
    else:
        await  message.answer(
            text='Добро пожаловать! Чем могу помочь?',
            reply_markup=get_main_keyboard()
        )