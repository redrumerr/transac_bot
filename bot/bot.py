import logging
import csv
import aiogram.exceptions
import psycopg2
import asyncio
import json
import os
import glob
import pandas as pd
from parser.parse_data import get_holders, get_downloads_path
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from openpyxl import Workbook


with open('secrets.json', 'r') as f:
    data = json.load(f)
    logging.info('Данные из json успешно загружены')

API_TOKEN = data['bot_api']
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


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
    elif callback_query.data == "instructions":
        await instructions(callback_query)
    elif callback_query.data == "transactions":
        await callback_query.answer("Функция в разработке.", show_alert=True)

        
def instructions_keyboard():
    """Меню инструкции."""
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Руководство по использованию", callback_data="manual"),
             InlineKeyboardButton(text="Видео-гайд", callback_data="video"),
             InlineKeyboardButton(text="Как разбить текст по столбцам в Excel", callback_data="excel")]
        ]
    )
    return inline_keyboard


@dp.callback_query(lambda c: c.data == "instructions")
async def instructions(callback_query: types.CallbackQuery):
    """Отправка инструкции."""
    await bot.send_message(
        callback_query.message.chat.id,
        "Выберите раздел инструкции",
        reply_markup=instructions_keyboard()
    )


@dp.callback_query(lambda c: c.data == "manual")
async def manual(callback_query: types.CallbackQuery):
    """Отправка руководства по использованию."""
    manual_text = """
    Руководство по использованию:
    1. Нажмите на кнопку "Владельцы", чтобы получить список владельцев выбранных вами криптовалют.
    2. Введите название или адрес криптовалют (например, Bitcoin или 0xF629...a3B9c).
    3. Выберите диапазон фильтрации в долларах для каждой монеты поочередно (например, 5000-9000, где 5000 - нижняя граница, 9000 - верхняя).
    4. Подтвердите введенные вами фильтры.
    5. Список владельцев выбранных монет будет отправлен вам в виде файла в формате CSV, который вы сможете открыть в Excel.
    """
    await bot.send_message(
        callback_query.message.chat.id,
        manual_text,
        reply_markup=main_menu_keyboard()
    )


@dp.callback_query(lambda c: c.data == "video")
async def video(callback_query: types.CallbackQuery):
    """Отправка видео-гайда.""" 
    await bot.send_message(
        callback_query.message.chat.id,
        "Видео-гайд доступен по следующей ссылке: https://www.youtube.com/shorts/yKS1yCk-aNs",
        reply_markup=main_menu_keyboard()
    )


@dp.callback_query(lambda c: c.data == "excel")
async def excel(callback_query: types.CallbackQuery):
    """Отправка инструкции по разбиению текста по столбцам в Excel."""
    images = [
        "bot/1.jpg", 
        "bot/2.jpg",
        "bot/3.jpg",
        "bot/4.jpg",
        "bot/5.jpg",
    ]
    for image in images:
        input_file = FSInputFile(image, filename=os.path.basename(image))
        await bot.send_photo(
            callback_query.message.chat.id,
            photo=input_file,
            caption="Шаг {}".format(images.index(image) + 1)
        )
    await bot.send_message(
        callback_query.message.chat.id,
        "Готово!",
        reply_markup=main_menu_keyboard()
    )


@dp.callback_query(lambda c: c.data == "instructions")
async def instructions(callback_query: types.CallbackQuery):
    """Отправка инструкции."""
    await bot.send_message(
        callback_query.message.chat.id,
        "Выберите раздел инструкции",
        reply_markup=instructions_keyboard()
    )
@dp.callback_query(lambda c: c.data == "manual")
async def manual(callback_query: types.CallbackQuery):
    """Отправка руководства по использованию."""
    manual_text = """
    Руководство по использованию:
    1. Нажмите на кнопку "Владельцы", чтобы получить список владельцев выбранных вами криптовалют.
    2. Введите название или адрес криптовалют (например, Bitcoin или 0xF629...a3B9c).
    3. Выберите диапазон фильтрации в долларах для каждой монеты поочередно (например, 5000-9000, где 5000 - нижняя граница, 9000 - верхняя).
    4. Подтвердите введенные вами фильтры.
    5. Список владельцев выбранных монет будет отправлен вам в виде файла в формате CSV, который вы сможете открыть в Excel.
    """
    await bot.send_message(
        callback_query.message.chat.id,
        manual_text,
        reply_markup=main_menu_keyboard()
    )
@dp.callback_query(lambda c: c.data == "video")
async def video(callback_query: types.CallbackQuery):
    """Отправка видео-гайда."""
    video_url = "https://www.youtube.com/shorts/yKS1yCk-aNs"  
    await bot.send_video(
        callback_query.message.chat.id,
        video_url,
        reply_markup=main_menu_keyboard()
    )
@dp.callback_query(lambda c: c.data == "excel")
async def excel(callback_query: types.CallbackQuery):
    """Отправка инструкции по разбиению текста по столбцам в Excel."""
    images = [
        "bot/1.jpg", 
        "bot/2.jpg",
        "bot/3.jpg",
        "bot/4.jpg",
        "bot/5.jpg",
    ]
    for image in images:
        input_file = FSInputFile(image, filename=os.path.basename(image))
        await bot.send_photo(
            callback_query.message.chat.id,
            photo=input_file,
            caption="Шаг {}".format(images.index(image) + 1)
        )
    await bot.send_message(
        callback_query.message.chat.id,
        "Готово!",
        reply_markup=main_menu_keyboard()
    )

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


async def merge_csv_files(directory, output_filename, required_coins):
    """Создает Excel-файл с кошельками, у которых есть все заданные монеты."""
    csv_files = glob.glob(f"{directory}/*.csv")
    if not csv_files:
        return None

    # Общий DataFrame для всех данных
    combined_data = pd.DataFrame()

    for file in csv_files:
        currency_name = os.path.basename(file).split('_')[0]
        try:
            data = pd.read_csv(file, encoding='cp1251')

            if len(data.columns) < 2:
                continue

            data.columns = ["Адрес кошелька", "Количество"] + data.columns.tolist()[2:]

            if "PendingBalanceUpdate" in data.columns:
                data.drop(columns="PendingBalanceUpdate", inplace=True)

            data["Название криптовалюты"] = currency_name
            data = data[["Адрес кошелька", "Название криптовалюты", "Количество"]]

            combined_data = pd.concat([combined_data, data], ignore_index=True)
        except Exception as e:
            print(f"Ошибка обработки файла {file}: {e}")

    if combined_data.empty:
        return None

    # Фильтрация данных: оставляем только кошельки, у которых есть все монеты из списка required_coins
    wallets_with_all_coins = (
        combined_data[combined_data["Название криптовалюты"].isin(required_coins)]
        .groupby("Адрес кошелька")
        .filter(lambda x: set(required_coins).issubset(set(x["Название криптовалюты"])))
    )

    if wallets_with_all_coins.empty:
        return None

    # Группировка по адресу кошелька и сбор данных
    grouped_data = (
        wallets_with_all_coins.groupby("Адрес кошелька")
        .apply(lambda x: {
            "Адрес кошелька": x["Адрес кошелька"].iloc[0],
            "Количество": ", ".join(f"{coin}: {amount}" for coin, amount in x.groupby("Название криптовалюты")["Количество"].sum().items())
        })
        .apply(pd.Series)
    )

    output_path = os.path.join(directory, output_filename)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        grouped_data.to_excel(writer, sheet_name="Совпадения", index=False)

    # Удаляем исходные CSV-файлы
    for file in csv_files:
        os.remove(file)

    return output_path


@dp.callback_query(lambda c: c.data == "confirm")
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    """Подтверждение фильтров и объединение файлов."""
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.answer('В процессе...')

    data = await state.get_data()
    crypto_data = data.get("crypto_data", [])
    required_coins = [crypto["currency_name"] for crypto in crypto_data]
    downloads_path = get_downloads_path()

    for crypto in crypto_data:
        try:
            currency_name = crypto["currency_name"]
            amount_filter_low = crypto["amount_filter_low"]
            amount_filter_up = crypto["amount_filter_up"]

            await get_holders(currency_name, amount_filter_low, amount_filter_up)
        except Exception as e:
            logging.exception(e)
            await callback_query.message.answer(f"Ошибка обработки {crypto['currency_name']}: {e}")

    merged_file_path = await merge_csv_files(downloads_path, "merged_cryptos.xlsx", required_coins)

    if merged_file_path:
        input_file = FSInputFile(merged_file_path)
        await bot.send_document(callback_query.from_user.id, input_file)
        os.remove(merged_file_path)
        await callback_query.message.answer("Все данные объединены и отправлены! Возвращаемся в главное меню...", reply_markup=types.ReplyKeyboardRemove())
    else:
        await callback_query.message.answer("Не удалось найти файлы для объединения.")

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
