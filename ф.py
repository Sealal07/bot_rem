import aiogram
from aiogram import Dispatcher,Bot,types,F
import logging
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.filters import CommandStart
import  asyncio


#1 конфигурация
logging.basicConfig(level=logging.DEBUG)

TOKEN ='8293020200:AAGNbitALAp80BMIB91nH4Mkc4dkihOwWGA'
bot= Bot(TOKEN)

dp = Dispatcher()
#2 обработчики
@dp.message(CommandStart())
async def send_welcome(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='нажми меня',
                              callback_data='demo')]
    ]
)
    await message.reply('Привет тебе, друг! Я тестовый бот' 'отправь любой текст или нажми кнопку',
                        reply_markup=keyboard)

@dp.callback_query(F.data('demo'))
async def callback_demo(call: CallbackQuery):
    await call.answer(
        text='спасибо за нажатие!это callback query'
    )
    await call.message.edit_text(
        'кнопка нажата'
    )

@dp.message()
async def echo(message: Message):
    await message.answer(f'**{message.text}** ты сказал')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('бот остановлен')