import logging
import csv

import aiogram.exceptions
import psycopg2
import asyncio
import json
import os
from parser.parse_data import get_holders, get_downloads_path
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
    await message.answer("Напишите цену в долларах для фильтра, например: 5000-20000")
    await state.set_state(Form.amount_filter)


@dp.message(Form.amount_filter)
async def process_amount_filter(message: types.Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        currency_name = state_data['currency_name']
        amount_filter_low, amount_filter_up = list(map(int, message.text.split('-'))) if message.text else [None, None]
    except ValueError:
        await message.answer("Некорректный формат фильтра. Попробуйте снова.")
        return await state.set_state(Form.amount_filter)

    sent_csv_path = f'{get_downloads_path()}\\{currency_name}_filter_{amount_filter_low}-{amount_filter_up}.csv'
    await state.update_data(currency_name=currency_name, amount_filter_low=amount_filter_low,
                            amount_filter_up=amount_filter_up, file_path=sent_csv_path)
    confirm_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
    )
    await message.answer("Подтвердите фильтр:", reply_markup=confirm_markup)


@dp.callback_query(lambda c: c.data == "confirm")
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.answer('В процессе...')
    state_data = await state.get_data()
    file_path = state_data['file_path']
    currency_name = state_data['currency_name']
    amount_filter_low = state_data['amount_filter_low']
    amount_filter_up = state_data['amount_filter_up']

    try:
        await get_holders(currency_name, amount_filter_low, amount_filter_up)
        if file_path is None or not os.path.exists(file_path):
            await callback_query.answer("Ошибка при обработке данных или файл не найден. Попробуйте снова.")
            return await state.set_state(Form.currency_name)
    except Exception as e:
        logging.exception(f"Произошла непредвиденная ошибка: {e}")
        await callback_query.answer(f"Произошла непредвиденная ошибка: {e}")

    try:
        input_file = FSInputFile(file_path)
        await bot.send_document(callback_query.from_user.id, input_file)
        os.remove(file_path)
        await state.clear()
    except FileNotFoundError:
        await callback_query.answer("Файл не найден!", show_alert=True)
    except aiogram.exceptions.TelegramBadRequest:
        pass
    except Exception as e:
        logging.exception(f"Ошибка при отправке файла: {e}")
        await callback_query.answer("Произошла ошибка при отправке файла!", show_alert=True)


@dp.callback_query(lambda c: c.data == "cancel")
async def process_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, 'Напишите цену в долларах для фильтра, например: 5000-20000')
    return await state.set_state(Form.amount_filter)


async def main():
    await dp.start_polling(bot)
