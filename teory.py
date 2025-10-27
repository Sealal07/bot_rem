import aiogram
from aiogram import Dispatcher

TOKEN = '8293020200:AAGNbitALAp80BMIB91nH4Mkc4dkihOwWGA'
bot = aiogram.Bot(TOKEN)

dp = Dispatcher(bot)

# Handlers
# Storage
# FSM (Finite state machine) -конечный автомат состояний

# start_polling()
# types
# logging

# @dp.message_handler(commands=['start', 'help'])
# @dp.message_handler(text='Привет')
# @dp.message_handler(content_types=['photo'])
# @dp.message_handler(text_contains='бот')
# @dp.callback_query_handler(text='buy')
# @dp.inline_handler()