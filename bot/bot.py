import logging
import csv
import psycopg2
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
import json

# Загрузка секретов
with open('secrets.json', 'r') as f:
    data = json.load(f)
    logging.info('Данные из json успешно загружены')

API_TOKEN = data['bot_api']
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подключение к базе данных
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

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext): # state добавлен сюда
    await message.answer("Привет! Я бот для отслеживания транзакций криптовалют. Введите название криптовалюты:")
    await state.set_state(Form.currency_name) # Изменено здесь

@dp.message(Form.currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    name = message.text

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT wallet_address, amount FROM wallets WHERE currency_name = %s', (name,))
    wallets = cursor.fetchall()
    cursor.close()
    conn.close()

    if wallets:
        csv_file = 'wallets_info.csv'
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Wallet Address', 'Amount'])
            for wallet in wallets:
                writer.writerow([wallet[0], wallet[1]])

        await message.answer("Данные успешно сохранены в файл wallets_info.csv")
    else:
        await message.answer("Криптовалюта не найдена в базе данных.")

    await state.clear()
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())