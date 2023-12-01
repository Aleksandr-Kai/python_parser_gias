import requests
import datetime
import time
import json
import pandas as pd

tenderNameShorts = {
    "Закупка из одного источника": "ЗОИ",
    "Электронный аукцион":"ЭА",
    "Запрос ценовых предложений":"ЗЦП"
}

headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=utf-8',
    'Origin': 'https://gias.by',
    'Pragma': 'no-cache',
    'Referer': 'https://gias.by/gias/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not=A?Brand";v="99", "Chromium";v="118"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

baseLink = 'https://gias.by/gias/#/purchase/current/'

def create_request_body(dtFrom, dtTo, searchStr='', page=0, pageSize=10):
    data = {
        'page': page,
        'pageSize': pageSize,
        'dtCreateFrom': int(time.mktime(dtFrom.timetuple())*1000),
        'dtCreateTo': int(time.mktime(dtTo.timetuple())*1000),
        'industry': [
            234,
            235,
            236,
        ],
        'sortField': 'dtCreate',
        'sortOrder': 'DESC',
    }
    if searchStr != '':
        data["contextTextSearch"] = searchStr
    return data

def parse(dtFrom, dtTo, searchStr):
    # json_data = create_request_body(datetime.datetime(2021, 7, 26, 21, 20),datetime.datetime.now())
    json_data = create_request_body(dtFrom, dtTo, searchStr)
    response = requests.post('https://gias.by/search/api/v1/search/purchases', headers=headers, json=json_data, verify=False)

    if response.status_code != 200:
        print(f"Request failed: {response.status_code}")
        return
    
    responseData = response.json()
    content = responseData["content"]

    with open('response.json', 'w') as file:
        file.write(json.dumps(responseData, indent=4, ensure_ascii=False))

    columns = parseJson(responseData["content"])
    df = pd.DataFrame({
        'Предмет закупки':columns[0],
        'Наименование заказчика/организатора закупки':columns[1],
        'Место нахождение':columns[2],
        'Номер':columns[3],
        'Ориент. стоимость':columns[4],
        'Предложения до':columns[5],
        'Время подачи':columns[6],
        'Тип закупки':columns[7],
        'Дата размещения':columns[8],
        'Номенклатура ED':columns[9],
        'Категории':columns[10],
        'Участие в закупке':columns[11],
        'Ответсвенный':columns[12]
    })
    df.to_excel(f'./tenders_{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.xlsx', sheet_name='Закупки', index=False)

def getTenderForm(url):
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    return tenderNameShorts[data["tenderFormName"]]

def parseJson(data):
    result = [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ]
    for item in data:
        url = f"{baseLink}{item['purchaseGiasId']}"
        result[0].append(url)
        result[1].append(item["organizator"]["name"])
        result[2].append(item["organizator"]["location"])
        result[3].append(item["publicPurchaseNumber"])
        result[4].append(item["sumLot"]["sumLot"])
        if item["requestDate"]:
            date = datetime.datetime.fromtimestamp(item["requestDate"]/1000)
            result[5].append(date.strftime("%d.%m.%Y"))
        else:
            result[5].append("-")
        result[6].append("-")
        tenderForm = getTenderForm(f"https://gias.by/purchase/api/v1/purchase/{item['purchaseGiasId']}")
        result[7].append(tenderForm) # purchaseType
        result[8].append(datetime.datetime.fromtimestamp(item["dtCreate"]/1000).strftime("%d.%m.%Y"))
        result[9].append("-")
        result[10].append("-")
        result[11].append("-")
        result[12].append("-")

    return result

def main():
    searchStr = input("Input search string or press Enter> ")
    dtFrom = input("Input date 'From' (1.12.2023)> ")
    dtTo = input("Input date 'To' (1.12.2023)> ")
    
    parse(datetime.datetime.strptime(dtFrom, "%d.%m.%Y") ,datetime.datetime.strptime(dtTo, "%d.%m.%Y"), searchStr)

    # with open('./response_.json') as file:
    #     jsonData = json.load(file)
    #     columns = parseJson(jsonData["content"])

    #     df = pd.DataFrame({
    #         'Предмет закупки':columns[0],
    #         'Наименование заказчика/организатора закупки':columns[1],
    #         'Место нахождение':columns[2],
    #         'Номер':columns[3],
    #         'Ориент. стоимость':columns[4],
    #         'Предложения до':columns[5],
    #         'Время подачи':columns[6],
    #         'Тип закупки':columns[7],
    #         'Дата размещения':columns[8],
    #         'Номенклатура ED':columns[9],
    #         'Категории':columns[10],
    #         'Участие в закупке':columns[11],
    #         'Ответсвенный':columns[12]
    #     })
    #     df.to_excel('./tenders.xlsx', sheet_name='Закупки', index=False)

if __name__ == "__main__":
    main()