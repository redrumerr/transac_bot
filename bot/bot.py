import logging
import csv
import psycopg2
import asyncio
import json
import os
from parser.parse_data import get_holders
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputFile


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

    try:
        downloaded_csv_path = await get_holders(currency_name, amount_filter)
        if downloaded_csv_path is None or not os.path.exists(downloaded_csv_path):
            await message.answer("Ошибка при обработке данных или файл не найден. Попробуйте снова.")
            return

        confirm_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")]
            ]
        )
        await message.answer("Подтвердите фильтр:", reply_markup=confirm_markup)
        await state.update_data(file_path=downloaded_csv_path)

        # await state.clear()

    except Exception as e:
        logging.exception(f"Произошла непредвиденная ошибка: {e}")
        await message.answer(f"Произошла непредвиденная ошибка: {e}")


@dp.callback_query(lambda c: c.data == "confirm")
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        file_path = data['file_path']
        input = FSInputFile(file_path)
        await bot.send_document(callback_query.from_user.id, input)

        await state.clear()
        await callback_query.answer() 
        await callback_query.message.delete() 
        
        os.remove(file_path)
    except FileNotFoundError:
        await callback_query.answer("Файл не найден!", show_alert=True)
    except Exception as e:
        logging.exception(f"Ошибка при отправке файла: {e}")
        await callback_query.answer("Произошла ошибка при отправке файла!", show_alert=True)

async def main():
    await dp.start_polling(bot)