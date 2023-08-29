import json
from time import sleep
from random import randint
import requests
import openpyxl
from aiogram import types
from bs4 import BeautifulSoup
from parsers.classes.proxies import ProxyManager

PROX = ProxyManager()

def request_decorator(func):
    def wrapper(f, **kwargs):
        a = True
        i = 1
        while a:
            response = func(f, **kwargs)
            print(response.status_code)
            if response.status_code == 200:
                sleep(randint(1, 2))
                a = False
            else:
                print(PROX.get_current())
                with open('resp.html', 'w', encoding='utf8') as file:
                    file.write(response.text)
                exit()
                PROX.next()

            if i > 30:
                raise Exception("Proxy don't work!")
            i += 1
        return response
    return wrapper


@request_decorator
def req(func, **kwargs):
    resp = func(**kwargs)
    return resp


def create_session():
    session = requests.Session()
    cookies = {
        '__cf_bm': 'YoQbzlehtc7L7vOOPgDdkFeNBbFzq2PFIIT9KyMc.SQ-1677365103-0-AYvVPBLOAqD3ewOdLqq+zqsMcSmHTp3u24aLjg6A8/kIPvG72DyRn3BRnktAl4hlZUD+K70dE7helMD2hEMRIRQ=',
    }

    headers = {
        'accept': '*/*',
        # 'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US',
        'apollographql-client-name': 'Iron',
        'apollographql-client-version': '2023.02.12.02',
        'app-platform': 'Iron',
        'app-version': '2023.02.12.02',
        # 'content-length': '1402',
        'content-type': 'application/json',
        'origin': 'https://stockx.com',
        'referer': 'https://stockx.com/',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'selected-country': 'TH',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'x-operation-name': 'GetSearchResults',
        'x-stockx-device-id': '0e1a3324-7f22-47f9-a552-f9eec36bba6c',
        # 'Cookie': '__cf_bm=YoQbzlehtc7L7vOOPgDdkFeNBbFzq2PFIIT9KyMc.SQ-1677365103-0-AYvVPBLOAqD3ewOdLqq+zqsMcSmHTp3u24aLjg6A8/kIPvG72DyRn3BRnktAl4hlZUD+K70dE7helMD2hEMRIRQ=',
    }

    session.headers.update(headers)
    session.cookies.update(cookies)
    return session


def get_sb():
    book = openpyxl.Workbook()
    sheet = book.worksheets[0]
    sheet.column_dimensions['A'].width = 50.71
    sheet.column_dimensions['C'].width = 29.43
    sheet.freeze_panes = 'A2'
    may = 'Name', 'Brand', 'Model', 'salesThisPeriod', 'salesLastPeriod', 'lastSale', 'lowestAsk', 'highestBid', 'urlKey', 'real_sku'
    sheet.append(may)
    return sheet, book


async def get_top(user_brand: str, msg: types.Message):
    session = create_session()
    sheet, book = get_sb()
    counter = 0
    await msg.edit_text(f'Выполнено 0%. (0/1000)')
    for page in range(1, 26):
        print("Взял страницу с номером " + str(page))
        json_data = {
            'query': 'query Browse($category: String, $filters: [BrowseFilterInput], $filtersVersion: Int, $query: String, $sort: BrowseSortInput, $page: BrowsePageInput, $currency: CurrencyCode, $country: String!, $market: String, $staticRanking: BrowseExperimentStaticRankingInput, $skipFollowed: Boolean!) {\n  browse(\n    category: $category\n    filters: $filters\n    filtersVersion: $filtersVersion\n    query: $query\n    sort: $sort\n    page: $page\n    experiments: {staticRanking: $staticRanking}\n  ) {\n    suggestions {\n      isCuratedPage\n      relatedPages {\n        title\n        url\n      }\n      locales\n    }\n    results {\n      edges {\n        objectId\n        node {\n          ... on Product {\n            ...BrowseProductDetailsFragment\n            ...FollowedFragment @skip(if: $skipFollowed)\n            ...ProductTraitsFragment\n            market(currencyCode: $currency) {\n              ...MarketFragment\n            }\n          }\n          ... on Variant {\n            id\n            followed @skip(if: $skipFollowed)\n            product {\n              ...BrowseProductDetailsFragment\n              traits(filterTypes: [RELEASE_DATE, RETAIL_PRICE]) {\n                name\n                value\n              }\n            }\n            market(currencyCode: $currency) {\n              ...MarketFragment\n            }\n            traits {\n              size\n            }\n          }\n        }\n      }\n      pageInfo {\n        limit\n        page\n        pageCount\n        queryId\n        queryIndex\n        total\n      }\n    }\n    query\n  }\n}\n\nfragment FollowedFragment on Product {\n  followed\n}\n\nfragment ProductTraitsFragment on Product {\n  productTraits: traits(filterTypes: [RELEASE_DATE, RETAIL_PRICE]) {\n    name\n    value\n  }\n}\n\nfragment MarketFragment on Market {\n  currencyCode\n  bidAskData(market: $market, country: $country) {\n    lowestAsk\n    highestBid\n    lastHighestBidTime\n    lastLowestAskTime\n  }\n  state(country: $country) {\n    numberOfCustodialAsks\n  }\n  salesInformation {\n    lastSale\n    lastSaleDate\n    salesThisPeriod\n    salesLastPeriod\n    changeValue\n    changePercentage\n    volatility\n    pricePremium\n  }\n  deadStock {\n    sold\n    averagePrice\n  }\n}\n\nfragment BrowseProductDetailsFragment on Product {\n  id\n  name\n  urlKey\n  title\n  brand\n  description\n  model\n  condition\n  productCategory\n  listingType\n  media {\n    thumbUrl\n    smallImageUrl\n  }\n}\n',
            'variables': {
                'query': '',
                'category': 'sneakers',
                'filters': [
                    {
                        'id': '_tags',
                        'selectedValues': [
                            user_brand,
                        ],
                    },
                    {
                        'id': 'browseVerticals',
                        'selectedValues': [
                            'sneakers',
                        ],
                    },
                ],
                'filtersVersion': 4,
                'sort': {
                    'id': 'most-active',
                    'order': 'DESC',
                },
                'page': {
                    'index': page,
                    'limit': 40,
                },
                'currency': 'USD',
                'country': 'TH',
                'marketName': None,
                'staticRanking': {
                    'enabled': False,
                },
                'skipFollowed': True,
            },
            'operationName': 'Browse',
        }
        response = req(session.post, url='https://stockx.com/api/p/e', json=json_data, proxies=PROX.get_current())

        need = response.json()
        if len(need['data']['browse']['results']['edges']) == 0:
            raise Exception('Данного бренда не найдено.')
        for citizen in range(0, 40):
            counter += 1
            print("Взял позицию с номером: " + str(citizen))
            
            node = need['data']['browse']['results']['edges'][citizen]['node']

            title = node['title']
            brand = node['brand']
            model = node['model']
            
            market = node['market']

            salesThisPeriod = market['salesInformation']['salesThisPeriod']
            salesLastPeriod = market['salesInformation']['salesLastPeriod']
            lastSale = market['salesInformation']['lastSale']
            lowestAsk = market['bidAskData']['lowestAsk']
            highestBid = market['bidAskData']['highestBid']
            
            urlKey = "https://stockx.com/" + node['urlKey']
            print("Ссылка: " + str(urlKey))

            url_card = req(session.get, url=urlKey, proxies=PROX.get_current())
            soup = BeautifulSoup(url_card.text, "lxml")
            try:
                real_sku = soup.find("p", class_="chakra-text css-wgsjnl").text
            except:
                real_sku = 'None'

            print("Артикул кроссовок: " + (real_sku))
            may = title, brand, model, salesThisPeriod, salesLastPeriod, lastSale, lowestAsk, highestBid, urlKey, real_sku
            sheet.append(may)
            book.save('top_sells.xlsx')
            print("Файл обновил")
            PROX.next()
            await msg.edit_text(f'Выполнено {(counter/10)}%. ({counter}/1000)')

def main():
    # filename = 'sku.xlsx'
    # userbrand = 'new balance'
    # get_top(userbrand, filename)
    sheet, book = get_sb()
    book.save('test.xlsx')


if __name__ == '__main__':
    main()
