from seleniumwire import webdriver
from selenium_cookies import CookieHandler

cookies = {  # без _ga_T1JC9RNQXV и cf_clearance не работает
    '_ga_T1JC9RNQXV': 'GS1.1.1732214781.10.1.1732216017.56.0.0',
    '_ga': 'GA1.2.1342471600.1731936902',
    'etherscan_offset_datetime': '+3',
    '_gid': 'GA1.2.2140093656.1732102175',
    'etherscan_switch_token_amount_value': 'value',
    'etherscan_cookieconsent': 'True',
    'ASP.NET_SessionId': 'ji4vku4afiz51hdrsstypzzv',
    '__cflb': '0H28vPcoRrcznZcNZSuFrvaNdHwh857EMRWdxhVJ6AY',
    'cf_clearance': 'S5.LeU3UYr4auKwg5ntyX4OKncwooZnot215Jh9TwJ0-1732216018-1.2.1.1-AbwIEuE9n_rcZpJKf5nDwsLzXCXnq0vFAREuD4GyTbqMsYylSV0X7t9rW2.h7yI4tj_eDZVJcacb6_ZCdeHoD4P02NqDSnM1dIOk4njL8sikpSBcU_F3I9bzAjeNR4lYB2at2V5Rqg3vgCS7Fpxb.zJw0eNIchKl1_gvX.RgcBHMNLHZbePRy4k0e7GloxHINhpoQql1f_06WVlhXyrscvkOq1mzCogRaJ4Fejf5t76JYe2rfaFpKClRjGM6ks3kzYcUt6PgH7CJxO3h2u0mXPP2t.SkC.YzxRyBChF3_q7A_NgQ0mcuywInOXX24A3dduRS2w0xLb70uWhX8lb0oLqZeJ4tr6i0TxQu9JOOfFwLB3EuQLOT5HFPNGZTC3yIPWoOMa2GcqDChOTgS6tRLA',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
}

cookies_price = {
    'cmc-language': 'en',
    'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%221934b762a1a245-0dbdc525034d0b8-f575722-1296000-1934b762a1b9f0%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkzNGI3NjJhMWEyNDUtMGRiZGM1MjUwMzRkMGI4LWY1NzU3MjItMTI5NjAwMC0xOTM0Yjc2MmExYjlmMCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%221934b762a1a245-0dbdc525034d0b8-f575722-1296000-1934b762a1b9f0%22%7D',
    'sajssdk_2015_cross_new_user': '1',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Thu+Nov+21+2024+18%3A00%3A13+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a6e5b2b7-cee4-4e43-a540-c96bb410c33c&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&groups=C0003%3A1%2CC0001%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&intType=1&geolocation=RU%3B',
    'OTGPPConsent': 'DBABLA~BVQqAAAACgA.QA',
    'OptanonAlertBoxClosed': '2024-11-20T21:24:34.300Z',
    'x-csrf-token': '810b2a52ac2dc871a1ea6fcce7fbec5726d94ba8717a88fc888f42a7784be73cf4972081245b4316d2ed79569af47e6657671f23a9d7abec18db66a65a1db3c1e687823d91be6773d869f2d6f6989fb707dad03dde4ae45b21a1da238b581832f0e140624cb305ea662cac451feadb89',
    '_sharedID': 'a763c883-e879-4a84-a1b4-fdd3f30d0fb4',
    '_sharedID_cst': 'zix7LPQsHA%3D%3D',
    '_cc_id': '15c3437585e37cb2d5cd68a5ca09851a',
    'panoramaId_expiry': '1732287614858',
    '__gads': 'ID=59542784e2021d6d:T=1732201215:RT=1732201795:S=ALNI_MZcoOJNILtt5kgjOz7tZ0usjB7MGA',
    '__gpi': 'UID=00000f9af089681a:T=1732201215:RT=1732201795:S=ALNI_MaYnIxNfScF07F5bUP078WJ0DC8Rg',
    '__eoi': 'ID=3ceb3b22f95193f0:T=1732201215:RT=1732201795:S=AA-AfjaRb8XzVV_vaUhneHid9Oz0',
}

headers_price = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://coinmarketcap.com/currencies/sushiswap/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
}


def get_cookies_etherscan():
    global cookies
    print('Getting cookies...')

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])

    driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''
    })

    cookie_handler = CookieHandler(driver,
                                   "https://etherscan.io/advanced-filter?tkn=0x6b3595068778dd592e39a122f4f5a5cf09c90fe2&txntype=2&amt=5000%7e999999999",
                                   overwrite=True, filename="get-stocks", wait_time=10)
    saved_cookies = cookie_handler.save_cookies()

    for e in saved_cookies:
        cookies[e['name']] = e['value']
    print(cookies)

