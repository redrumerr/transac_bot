import logging
import csv
import psycopg2
import asyncio
import json
from parser.parse_data import get_holders
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


with open('secrets.json', 'r') as f:
    data = json.load(f)
    logging.info('Данные из json успешно загружены')

API_TOKEN = data['bot_api']
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def connect_db():
    return psycopg2.connect(
        dbname=data['dbname'],
        user=data['user'],
        password=data['password'],
        host=data['host'],
        port=data['port']
    )

class Form(StatesGroup):
    currency_name = State()  
    amount_filter = State()  


@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название криптовалюты (например, Bitcoin):")
    await state.set_state(Form.currency_name)


@dp.message(Form.currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.strip()  
    await state.update_data(currency_name=currency_name) 
    await message.answer("Укажите фильтр по количеству (например, 10, или оставьте пустым):")
    await state.set_state(Form.amount_filter)


@dp.message(Form.amount_filter)
async def process_amount_filter(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()  
        currency_name = data['currency_name']  
        amount_filter = int(message.text) if message.text else 0  
    except ValueError:
        await message.answer("Некорректный формат фильтра. Попробуйте снова.")
        return await state.set_state(Form.amount_filter)

    await get_holders(currency_name, amount_filter)  

    filename = f"{currency_name}_transactions_{amount_filter}.csv" if amount_filter else f"{currency_name}_transactions.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Wallet Address', 'Token Amount'])

    confirm_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{filename}")]
        ]
    )
    await message.answer("Подтвердите фильтр:", reply_markup=confirm_markup)
    await state.clear()


@dp.callback_query()
async def confirm_filter(callback_query: types.CallbackQuery, state: FSMContext):
    filename = callback_query.data.replace("confirm_", "")
    try:
        with open(filename, 'rb') as file:
            await bot.send_document(chat_id=callback_query.message.chat.id, document=file)
            await callback_query.answer("Файл отправлен.")
    except FileNotFoundError:
        await callback_query.answer("Файл не найден!")


async def main():
    await dp.start_polling(bot)