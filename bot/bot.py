import logging
import csv
import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.fsm import FSMContext, State, StatesGroup
from aiogram import Router
from aiogram.filters import Command
from aiogram.utils import executor
import json

with open ('secrets.json', 'r') as f:
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
        host=data['host']
    )


class Form(StatesGroup):
    currency_name = State()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Введите название криптовалюты:")
    await Form.currency_name.set()

@dp.message(State(Form.currency_name))
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

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)