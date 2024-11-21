import requests

cookies = {
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://coinmarketcap.com/currencies/shiba-inu/',
    'Connection': 'keep-alive',
    # 'Cookie': 'cmc-language=en; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221934b762a1a245-0dbdc525034d0b8-f575722-1296000-1934b762a1b9f0%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkzNGI3NjJhMWEyNDUtMGRiZGM1MjUwMzRkMGI4LWY1NzU3MjItMTI5NjAwMC0xOTM0Yjc2MmExYjlmMCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%221934b762a1a245-0dbdc525034d0b8-f575722-1296000-1934b762a1b9f0%22%7D; sajssdk_2015_cross_new_user=1; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Nov+21+2024+18%3A00%3A13+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a6e5b2b7-cee4-4e43-a540-c96bb410c33c&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&groups=C0003%3A1%2CC0001%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&intType=1&geolocation=RU%3B; OTGPPConsent=DBABLA~BVQqAAAACgA.QA; OptanonAlertBoxClosed=2024-11-20T21:24:34.300Z; x-csrf-token=810b2a52ac2dc871a1ea6fcce7fbec5726d94ba8717a88fc888f42a7784be73cf4972081245b4316d2ed79569af47e6657671f23a9d7abec18db66a65a1db3c1e687823d91be6773d869f2d6f6989fb707dad03dde4ae45b21a1da238b581832f0e140624cb305ea662cac451feadb89; _sharedID=a763c883-e879-4a84-a1b4-fdd3f30d0fb4; _sharedID_cst=zix7LPQsHA%3D%3D; _cc_id=15c3437585e37cb2d5cd68a5ca09851a; panoramaId_expiry=1732287614858; __gads=ID=59542784e2021d6d:T=1732201215:RT=1732201795:S=ALNI_MZcoOJNILtt5kgjOz7tZ0usjB7MGA; __gpi=UID=00000f9af089681a:T=1732201215:RT=1732201795:S=ALNI_MaYnIxNfScF07F5bUP078WJ0DC8Rg; __eoi=ID=3ceb3b22f95193f0:T=1732201215:RT=1732201795:S=AA-AfjaRb8XzVV_vaUhneHid9Oz0',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

response = requests.get('https://coinmarketcap.com/currencies/sushiswap/', cookies=cookies, headers=headers)

print(response.text)
