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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

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
    crypto_count = State()
    currency_name = State()
    amount_filter = State()
    confirmation = State()

def main_menu_keyboard():
    """Клавиатура для главного меню."""
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Транзакции", callback_data="transactions"),
             InlineKeyboardButton(text="Владельцы", callback_data="holders"),
             InlineKeyboardButton(text="Инструкция", callback_data="instructions")]
        ]
    )
    return inline_keyboard

async def show_main_menu(message: types.Message):
    """Отображаем меню пользователю."""
    await message.answer("Выберите действие:", reply_markup=main_menu_keyboard())

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    """Команда /start - показывает меню при запуске."""
    await show_main_menu(message)
    await state.clear()

@dp.callback_query(lambda c: c.data in ["transactions", "holders", "instructions"])
async def in_development(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка кнопок, находящихся в разработке."""
    if callback_query.data == "holders":
        await handle_holders(callback_query, state)
    elif callback_query.data == "transactions":
        await callback_query.answer("Функция в разработке.", show_alert=True)
    else:
        await callback_query.answer("Функция в разработке.", show_alert=True)

@dp.callback_query(lambda c: c.data == "holders")
async def handle_holders(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Владельцы'."""
    await callback_query.answer()
    await callback_query.message.answer(
        "Сколько криптовалют вы хотите ввести?",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Form.crypto_count)

@dp.message(Form.crypto_count)
async def process_crypto_count(message: types.Message, state: FSMContext):
    """Шаг: Получаем количество криптовалют и переходим к следующему этапу."""
    try:
        count = int(message.text.strip())
        if count <= 0:
            raise ValueError("Количество должно быть положительным числом.")
        await state.update_data(crypto_count=count, current_index=0, crypto_data=[])
        await message.answer("Введите название или адрес криптовалюты (например, Bitcoin или 0xF629...a3B9c):")
        await state.set_state(Form.currency_name)
    except ValueError:
        await message.answer("Некорректное количество. Пожалуйста, введите положительное целое число.")

@dp.message(Form.currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    """Шаг: Получаем название криптовалюты."""
    data = await state.get_data()
    crypto_data = data.get("crypto_data", [])
    crypto_data.append({"currency_name": message.text.strip()})
    await state.update_data(crypto_data=crypto_data)
    await message.answer("Напишите цену в долларах для фильтра, например: 5000-20000 или просто 5000")
    await state.set_state(Form.amount_filter)

@dp.message(Form.amount_filter)
async def process_amount_filter(message: types.Message, state: FSMContext):
    """Шаг: Получаем фильтр для текущей криптовалюты."""
    try:
        data = await state.get_data()
        crypto_data = data.get("crypto_data", [])
        current_crypto = crypto_data[-1]

        if '-' in message.text:
            amount_filter_low, amount_filter_up = map(int, message.text.strip().split('-'))
        else:
            amount_filter_low = int(message.text.strip())
            amount_filter_up = 99999999

        current_crypto.update({
            "amount_filter_low": amount_filter_low,
            "amount_filter_up": amount_filter_up
        })
        await state.update_data(crypto_data=crypto_data)

        # Проверяем, закончили ли ввод всех криптовалют
        current_index = data.get("current_index", 0) + 1
        crypto_count = data.get("crypto_count", 0)

        if current_index < crypto_count:
            await state.update_data(current_index=current_index)
            await message.answer(f"Введите название криптовалюты {current_index + 1}:")
            await state.set_state(Form.currency_name)
        else:
            await message.answer("Все данные введены. Подтвердите ввод:")
            for crypto in crypto_data:
                await message.answer(
                    f"Криптовалюта: {crypto['currency_name']}, Фильтр: {crypto['amount_filter_low']}-{crypto['amount_filter_up']}"
                )
            confirm_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
                    [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
                ]
            )
            await message.answer("Подтвердите введённые данные:", reply_markup=confirm_markup)
            await state.set_state(Form.confirmation)
    except ValueError:
        await message.answer(
            "Некорректный формат фильтра. Напишите цену в долларах, например: 5000-20000 или просто 5000."
        )

@dp.callback_query(lambda c: c.data == "confirm")
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    """Подтверждение фильтров и обработка данных."""
    # Удаляем сообщение подтверждения
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

    # Получаем все данные пользователя
    await callback_query.answer('В процессе...')
    data = await state.get_data()
    crypto_data = data.get("crypto_data", [])

    for crypto in crypto_data:
        try:
            currency_name = crypto["currency_name"]
            amount_filter_low = crypto["amount_filter_low"]
            amount_filter_up = crypto["amount_filter_up"]

            file_path = f"{get_downloads_path()}\\{currency_name}_filter_{amount_filter_low}-{amount_filter_up}.csv"
            await get_holders(currency_name, amount_filter_low, amount_filter_up)
            input_file = FSInputFile(file_path)
            await bot.send_document(callback_query.from_user.id, input_file)
            os.remove(file_path)
        except Exception as e:
            logging.exception(e)
            await callback_query.message.answer(f"Ошибка обработки {crypto['currency_name']}: {e}")

    # Возвращаем пользователя в главное меню
    await callback_query.message.answer(
        "Все файлы отправлены! Возвращаемся в главное меню...",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await show_main_menu(callback_query.message)
    await state.clear()

@dp.callback_query(lambda c: c.data == "cancel")
async def cancel_operation(callback_query: types.CallbackQuery, state: FSMContext):
    """Отмена операции и возврат в главное меню."""
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.message.answer("Операция отменена. Возвращаемся в главное меню...", reply_markup=types.ReplyKeyboardRemove())
    await show_main_menu(callback_query.message)
    await state.clear()

async def main():
    """Основной цикл запуска бота."""
    await dp.start_polling(bot)
