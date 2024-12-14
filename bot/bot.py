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
    currency_name = State()
    amount_filter = State()


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
        "Введите название или адрес криптовалюты (например, Bitcoin или 0xF629...a3B9c):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Form.currency_name)


@dp.message(Form.currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    """Шаг: Получаем название криптовалюты и переходим к следующему этапу."""
    currency_name = message.text.strip().replace(' ', '-')
    await state.update_data(currency_name=currency_name)
    await message.answer("Напишите цену в долларах для фильтра, например: 5000-20000 или просто 5000")
    await state.set_state(Form.amount_filter)


@dp.message(Form.amount_filter)
async def process_amount_filter(message: types.Message, state: FSMContext):
    """Шаг: Получаем фильтр и подтверждаем операцию."""
    try:
        state_data = await state.get_data()
        currency_name = state_data['currency_name']
        amount_filter_low, amount_filter_up = (None, None)
        if '-' in message.text:
            amount_filter_low, amount_filter_up = list(map(int, message.text.strip().split('-')))
        else:
            amount_filter_low = int(message.text.strip())
            amount_filter_up = 99999999
    except ValueError:
        await message.answer(
            "Некорректный формат фильтра. Напишите цену в долларах, например: 5000-20000 или просто 5000."
        )
        return await state.set_state(Form.amount_filter)

    sent_csv_path = f"{get_downloads_path()}\\{currency_name}_filter_{amount_filter_low}-{amount_filter_up}.csv"
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
    """Подтверждение фильтра и отправка данных."""
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.answer('В процессе...')
    state_data = await state.get_data()
    file_path = state_data['file_path']

    try:
        await get_holders(
            state_data['currency_name'],
            state_data['amount_filter_low'],
            state_data['amount_filter_up']
        )
        input_file = FSInputFile(file_path)
        await bot.send_document(callback_query.from_user.id, input_file)
        os.remove(file_path)

        # Кнопка для возврата в меню
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Вернуться к меню")]],
            resize_keyboard=True
        )
        await callback_query.message.answer(
            "Файл отправлен! Нажмите 'Вернуться к меню', чтобы продолжить.",
            reply_markup=keyboard
        )
        await state.clear()
    except Exception as e:
        logging.exception(e)
        await callback_query.answer(f"Ошибка: {e}", show_alert=True)


@dp.message(lambda message: message.text == "Вернуться к меню")
async def return_to_main_menu(message: types.Message, state: FSMContext):
    """Возврат в главное меню."""
    await show_main_menu(message)
    await state.clear()


@dp.callback_query(lambda c: c.data == "cancel")
async def cancel_filter(callback_query: types.CallbackQuery, state: FSMContext):
    """Отмена фильтра и возврат пользователя на предыдущий шаг."""
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.message.answer(
        "Введите цену в долларах для фильтра, например: 5000-20000 или просто 5000"
    )
    await state.set_state(Form.amount_filter)


async def main():
    """Основной цикл запуска бота."""
    await dp.start_polling(bot)
