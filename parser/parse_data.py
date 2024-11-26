import time
import re
import requests
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import json
import tqdm
from bs4 import BeautifulSoup
from parser.cookies_headers import cookies, headers, cookies_price, headers_price, \
                                    get_cookies_etherscan
from parser.forbidden_keywords import keywords


def main_parse():
    with ThreadPoolExecutor(max_workers=1) as executor:  # надо будет переписать на другую библу
        future_res = (executor.submit(parse_data, page) for page in range(1, 401))
        for future in concurrent.futures.as_completed(future_res):
            try:
                data = future.result()
                print(data)
            except Exception as e:
                print(e)
    pass


def parse_data(page):  # на параметр не смотри он духом силен (потом там будет другое)
    current_price = get_current_price()
    print(current_price)
    url = f'https://etherscan.io/advanced-filter?tkn=0x6b3595068778dd592e39a122f4f5a5cf09c90fe2&txntype=2&amt={5_000 // current_price}%7e999999999'
    print(url)
    response = requests.get(url, cookies=cookies, headers=headers)
    print(response)
    while response.status_code != 200:
        get_cookies_etherscan()
        response = requests.get(
            f'https://etherscan.io/advanced-filter?tkn=0x6b3595068778dd592e39a122f4f5a5cf09c90fe2&txntype=2&amt={5_000 // current_price}%7e999999999',
            cookies=cookies,
            headers=headers
        )
        print(response)
    print('Response.status_code:', response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')
    transactions_soup = BeautifulSoup(str(soup.find_all('tbody', class_='align-middle text-nowrap')), 'html.parser')
    transactions = list(map(str, transactions_soup.find_all('tr')))

    """ Приводим оставшиеся транзакции в понятный и приятный вид"""
    with ThreadPoolExecutor(max_workers=10) as executor_form:
        future_result = (executor_form.submit(form_data, transaction) for transaction in transactions)
        for future in concurrent.futures.as_completed(future_result):
            try:
                data = future.result()
                print(data)
            except Exception as e:
                print(e)

    exit(0)


def get_current_price():
    response = requests.get('https://coinmarketcap.com/currencies/sushiswap/',  # Находим страницу нужной криптовалюты на CoinMarketCap
                            cookies=cookies_price, headers=headers_price)
    soup = BeautifulSoup(response.text, 'html.parser')

    price = float(re.findall('\$[\d.]+', str(soup.find_all('span', class_='sc-65e7f566-0 WXGwg base-text')[0]))[0][1:])  # Находим цену на странице и преобразуем её
    return price


def check_keywords(string_to_be_checked):  # unused
    pattern = '(?:{})'.format('|'.join(keywords))  # паттерн для поиска слов, например: (?:Router|Binance|Mask)
    return bool(re.search(pattern, string_to_be_checked, flags=re.I))


def form_data(transaction_html):
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
    