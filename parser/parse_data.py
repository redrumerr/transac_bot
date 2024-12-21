import pyautogui
import webbrowser
import asyncio
import requests
import os
import csv
import json
import time
from parser.cookies_headers_urls import cookies_price, headers_price, url, cookies_eth, headers_eth
from parser.get_download_path import get_downloads_path
import re

pyautogui.FAILSAFE = True


async def get_holders(token_name: str, lower_limit: int = 5000, upper_limit: int = 9999999999):
    current_price, token_address = await get_current_price(token_name)
    sent_csv_path = f'{get_downloads_path()}\\{token_name}_filter_{lower_limit}-{upper_limit}.csv'
    lower_limit /= current_price
    upper_limit /= current_price

    while True:
        try:
            pyautogui.moveTo(1918, 200)
            webbrowser.register('Opera', None,
                                webbrowser.BackgroundBrowser(
                                    'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Opera\\opera.exe'))
            webbrowser.get('Opera').open(url, new=0)
            pyautogui.moveTo(668, 761,
                             4)  # наводимся на строку ввода токена ||| 2к: 668, 1042 ||| fullhd: 668, 761 ||| fullpizdec: 146, 603 ||| polyakov komp: 587, 486, 489, 692
            pyautogui.click()
            pyautogui.write(token_address, 0.05)
            pyautogui.scroll(-315)
            pyautogui.sleep(1)
            pyautogui.click()
            time.sleep(10)
            os.system("taskkill /f /im opera.exe")
            break
        except Exception as e:
            print(f"Error: {e}, retrying...")
            time.sleep(5)

    downloaded_csv_path = f'{get_downloads_path()}\export-tokenholders-for-contract-{token_address}.csv'
    try:
        with open(downloaded_csv_path, 'r') as csv_file:
            fieldnames = ('HolderAddress', 'Balance', 'PendingBalanceUpdate')
            reader = csv.DictReader(csv_file, fieldnames)
            with open(sent_csv_path, 'w', newline='', encoding='cp1251') as file:
                writer = csv.writer(file)
                field = ['Адрес владельца', 'Количество']
                writer.writerow(field)
                for row in reader:
                    try:
                        if lower_limit <= float(''.join(row['Balance'].split(','))) <= upper_limit:
                            writer.writerow(
                                [row['HolderAddress'],
                                 round(float(''.join(row['Balance'].split(','))) * current_price, 2)])
                    except ValueError:
                        pass
        os.remove(downloaded_csv_path)
        return sent_csv_path
    except FileNotFoundError:
        print("Файл не найден")
        return None
    except Exception as e:
        print(e)


async def get_current_price(token_name: str):
    response = requests.get(f'https://coinmarketcap.com/currencies/{token_name.lower()}/',
                            cookies=cookies_price, headers=headers_price)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        token_address = re.findall('contractAddress":"0x[\da-zA-Z\-\s]+', str(soup))[0][18:]
    except IndexError:
        response = requests.get(f'https://etherscan.io/token/{token_name.lower()}',
                                cookies=cookies_eth,
                                headers=headers_eth,
                                )
        price = float(re.findall('price": "[\d.]+', response.text)[0][9:])
        token_address = token_name.lower()
        return price, token_address

    price = float(re.findall('\$[\d.]+', str(soup.find_all('span', class_='sc-65e7f566-0 WXGwg base-text')[0]))[0][1:])
    return price, token_address
