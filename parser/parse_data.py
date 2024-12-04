import pyautogui
import webbrowser
import asyncio
import requests
import os
import csv
import json
import time

pyautogui.FAILSAFE = True


async def get_holders(token_address: str, url: str, lower_limit: int = 5000):
    current_price = await get_current_price(token_address)
    lower_limit = lower_limit / current_price
    webbrowser.register('Firefox', None,
                        webbrowser.BackgroundBrowser('C:\\Program Files\\Mozilla Firefox\\firefox.exe'))
    webbrowser.get(using='Firefox').open(url, new=0)
    pyautogui.moveTo(668, 1042, 4)  # наводимся на строку ввода токена
    pyautogui.click()
    pyautogui.write(token_address)  # вводим адрес токена
    pyautogui.moveTo(668, 1558, 3)  # наводимся на загрузку csv
    pyautogui.click()
    time.sleep(25)
    os.system("taskkill /f /im firefox.exe")
    downloaded_csv_path = f'C:\\Users\\Александр\\Downloads\\export-tokenholders-for-contract-{token_address}.csv'
    i = 0
    with open(downloaded_csv_path, 'r') as csv_file:
        fieldnames = ('HolderAddress', 'Balance', 'PendingBalanceUpdate')
        reader = csv.DictReader(csv_file, fieldnames)
        for row in reader:
            # if int(row['balance'])
            print(row)
    time.sleep(5)
    print(i)
    os.remove(downloaded_csv_path)


async def get_current_price(token_address: str):
    response = requests.get('https://coinmarketcap.com/currencies/sushiswap/',
                            # Находим страницу нужной криптовалюты на CoinMarketCap
                            cookies=cookies_price, headers=headers_price)
    soup = BeautifulSoup(response.text, 'html.parser')

    price = float(re.findall('\$[\d.]+', str(soup.find_all('span', class_='sc-65e7f566-0 WXGwg base-text')[0]))[0][
                  1:])  # Находим цену на странице и преобразуем её
    return price


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
