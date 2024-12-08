import pyautogui
import webbrowser
import asyncio
import requests
import os
import csv
import json
import time
from parser.cookies_headers_urls import cookies_price, headers_price, url
from bs4 import BeautifulSoup
import re

pyautogui.FAILSAFE = True


async def get_holders(token_name: str, lower_limit: int = 5000):
    current_price, token_address = await get_current_price(token_name)
    lower_limit /= current_price
    webbrowser.open(url, new=0)
    pyautogui.moveTo(668, 527, 4)  # наводимся на строку ввода токена
    pyautogui.click()
    pyautogui.write(token_address)  # вводим адрес токена
    pyautogui.moveTo(574, 787, 3)  # наводимся на загрузку csv
    pyautogui.click()
    time.sleep(15)
    # os.system("taskkill /f /im firefox.exe")  # прописать под используемый браузер
    downloaded_csv_path = f'C:\\Users\\alexp\\Downloads\\export-tokenholders-for-contract-{token_address}.csv'
    with open(downloaded_csv_path, 'r') as csv_file:
        fieldnames = ('HolderAddress', 'Balance', 'PendingBalanceUpdate')
        reader = csv.DictReader(csv_file, fieldnames)
        for row in reader:
            try:
                if float(''.join(row['Balance'].split(','))) >= lower_limit:
                    print(row)
            except ValueError:
                pass
    time.sleep(3)
    os.remove(downloaded_csv_path)


async def get_current_price(token_name: str):  # token_name вводится Михой
    response = requests.get(f'https://coinmarketcap.com/currencies/{token_name.lower()}/',
                            # Находим страницу нужной криптовалюты на CoinMarketCap
                            cookies=cookies_price, headers=headers_price)
    soup = BeautifulSoup(response.text, 'html.parser')

    token_address = re.findall('contractAddress":"0x[\da-zA-Z]+', str(soup))[0][18:]
    price = float(re.findall('\$[\d.]+', str(soup.find_all('span', class_='sc-65e7f566-0 WXGwg base-text')[0]))[0][
                  1:])  # Находим цену на странице и преобразуем её
    return price, token_address


async def form_data(transaction_html):
    date_time = re.findall('="[\d\-\s:]+"', transaction_html)[0][2:-1]
    from_address, to_address = re.findall('" data-highlight-target="0x[\da-z]+"', transaction_html)[:-1]
    from_address, to_address = from_address[25:-1], to_address[25:-1]
    transaction_hash = re.findall('tx/0x[\da-z]+', transaction_html)[0][3:]
    amount, dollar_price = re.findall('[\d,.\s]+\|[\d\s$.,]+', transaction_html)[0].split(' | ')
    dollar_price = dollar_price[1:]
    json_data = {'Дата время': date_time,  # вот эту хуйню пихай в бд, в соответствующие столбцы
                 'Адрес отправителя': from_address,
                 'Адрес получателя': to_address,
                 'Хэш транзакции': transaction_hash,
                 'Количество': float(''.join(amount.split(','))),
                 'Цена в долларах': float(''.join(dollar_price.split(',')))
                 }
    print(json_data)

    import database.database as db
    db.add_transaction(json_data)

    return json_data
