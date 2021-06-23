#!/usr/bin/env python
"""

Prices module

"""
from datetime import date


# mongodb+srv://sngoube:<password>@cluster0.jaxrk.mongodb.net/<dbname>?retryWrites=true&w=majority
# mongodb+srv://sngoube:Came1roun*@cluster0.jaxrk.mongodb.net/asset_analytics?retryWrites=true&w=majority
# pip install dnspython==2.0.0

# requirements
# dnspython
# Cython==0.29.17
# setuptools==49.6.0
# statsmodels==0.11.1
# fbprophet
# pandas
# numpy
# matplotlib
# plotly
# pymongo
# pymongo[srv]
# alpha_vantage
# requests
# u8darts


def load_exchange_list():
    import pandas as pd
    import requests
    from pymongo import MongoClient
    import json
    import os
    import re
    #jCJpZ8tG7Ms3iF0l
    eod_key = "60241295a5b4c3.00921778"
    # https://eodhistoricaldata.com/api/exchanges-list/?api_token=60241295a5b4c3.00921778&fmt=json

    collection_name = "exchanges"
    db_name = "asset_analytics"
    req = requests.get("https://eodhistoricaldata.com/api/exchanges-list/?api_token=60241295a5b4c3.00921778&fmt=json")
    list_exchange = req.json()

    access_db = "mongodb+srv://sngoube:Yqy8kMYRWX76oiiP@cluster0.jaxrk.mongodb.net/asset_analytics?retryWrites=true&w=majority"
    server = MongoClient(access_db)

    if collection_name in server[db_name].list_collection_names():
        server[db_name][collection_name].drop()
    server[db_name][collection_name].insert_many(list_exchange)
    print("Disconnected!")
    server.close()

def remove_special_car(d):
    nd = dict()
    for k, v in d.items():
        nk = k.replace('.', '')
        nd[nk] = remove_special_car(v) if isinstance(v, dict) else v
    return nd


def load_stock_universe():

    import pandas as pd
    import requests
    import json
    df_stocks = pd.read_csv("./asset_list.csv", sep=';', keep_default_na=False)
    ddf2 = pd.read_csv("./Global_Stock_Exchanges.csv", sep=',', keep_default_na=False)

    # Mapping bloomberg exchange code to EOD exchange code.
    dict_list = ddf2.to_dict(orient='records')
    dict_eod_bloom = dict()
    for mp in dict_list:
        bb = mp['Bloomberg Exchange Code']
        dict_eod_bloom[bb] = {"ExchangeCode": mp['EOD code'], "Country": mp['Country']}

    # Adding composite exchange codes:
    dict_eod_bloom['GR'] = {"ExchangeCode": dict_eod_bloom['GY']['ExchangeCode'],
                            "Country": dict_eod_bloom['GY']['Country']}
    dict_eod_bloom['SW'] = {"ExchangeCode": dict_eod_bloom['SE']['ExchangeCode'],
                            "Country": dict_eod_bloom['SE']['Country']}
    dict_eod_bloom['US'] = {"ExchangeCode": dict_eod_bloom['UQ']['ExchangeCode'],
                            "Country": dict_eod_bloom['UQ']['Country']}
    dict_eod_bloom['CN'] = {"ExchangeCode": dict_eod_bloom['CT']['ExchangeCode'],
                            "Country": dict_eod_bloom['CT']['Country']}

    stock_list = [] = []
    dict_stock_prim_listing = df_stocks.to_dict(orient='records')
    for pl in dict_stock_prim_listing:
        bb = pl['Exchange']
        pl['ExchangeCode'] = dict_eod_bloom[bb]['ExchangeCode']
        pl['Country'] = dict_eod_bloom[bb]['Country']
        stock_list.append(pl)
        #list_stock_prim_listing.append('{}.{}'.format(pl['ISIN'], dict_eod_bloom[pl['Bloomberg Exchange Code']]))


    my_list_of_stocks = df_stocks['ISIN'].tolist()

    # https://eodhistoricaldata.com/api/exchange-symbol-list/{EXCHANGE_CODE}?api_token={YOUR_API_KEY}
    #country_list = ['US', 'LSE', 'XETRA', 'VI', 'MI', 'PA', 'BR', 'SW', 'LU', 'MC', 'AS', 'LS', 'ST',
    #                'CO', 'OL', 'HK', 'TA', 'SW', 'FOREX', 'FOREX', 'ETLX' , 'INDX', 'CC']

    #'ISIN','Currency','Exchange','ETF Underlying Index Ticker', 'Dvd Freq', 'Code', 'Type','Name', 'GICS Sector','GICS Ind Name'
    #'Code', 'Name', 'Country', 'Exchange', 'Currency', 'Type', 'ISIN'

    """ 
    final_df = pd.DataFrame()
    for xcode in country_list:
        req = requests.get(
            "https://eodhistoricaldata.com/api/exchange-symbol-list/{}?api_token=60241295a5b4c3.00921778&fmt=json".format(
                xcode)
        )
        data = req.json()
        df_exchange_stocks = pd.DataFrame.from_dict(data)
        df_exchange_stocks.columns = ['Code', 'Name', 'Country', 'Exchange', 'Currency', 'Type', 'ISIN']
        df_exchange_stocks['ExchangeCode'] = xcode
        df_exchange_stocks.index = df_exchange_stocks['ISIN']
        final_df = final_df.append(df_exchange_stocks.loc[df_exchange_stocks['ISIN'].isin(my_list_of_stocks)])
    """
    #final_df.drop_duplicates(subset="ISIN", inplace=True)
    final_df = pd.DataFrame(stock_list)
    final_df.to_csv("./stock_universe.csv")


def is_valid_json(obj):

    try:
        stock_data = obj.json()
        tt = stock_data['General']
    except:
        print("Unable to serialize the object {}".format(obj))
        return False

    return True


def get_universe(name="", country="", type=""):
    import pandas as pd
    from pymongo import MongoClient


    collection_name = "stock_universe"
    db_name = "asset_analytics"
    access_db = "mongodb+srv://sngoube:Yqy8kMYRWX76oiiP@cluster0.jaxrk.mongodb.net/asset_analytics?retryWrites=true&w=majority"
    server = MongoClient(access_db)

    query = {"Name": {"$regex": '/*{}/*'.format(name), "$options": 'i'},
             "Country": {"$regex": '/*{}/*'.format(country), "$options": 'i'},
             "Type": {"$regex": '/*{}/*'.format(type), "$options": 'i'}
             }

    res = server[db_name][collection_name].find(query)

    print("Query {}".format(query))

    lres = list(res)

    item_list = []
    result = []
    if len(lres) > 0:
        print(' result {}'.format(lres))
        df = pd.DataFrame(lres)
        print(' df {}'.format(df))
        df = df[['ISIN', 'Code', 'Name', 'Country', 'Exchange', 'Currency', 'Type', 'ExchangeCode', 'logo']]
        # print(format(df.to_json(orient='records')))
        server.close()
        print(' result {}'.format(df))
        # result = df.to_json(orient='records')
        #result = df.to_dict(orient='records')
        #print('json result {}'.format(result))
    return df


def load_equity_etf_list():
    import pandas as pd
    import requests
    from pymongo import MongoClient
    import json
    import os
    import re
    #jCJpZ8tG7Ms3iF0le
    eod_key = "60241295a5b4c3.00921778"
    # https://eodhistoricaldata.com/api/exchanges-list/?api_token=60241295a5b4c3.00921778&fmt=json
    ddf = pd.read_csv("../asset_prices/stock_universe.csv", sep=',', keep_default_na=False)
    ddf = ddf[['ISIN','Code','Name','Country','Exchange','Currency','Type','ExchangeCode',
               'ETF Underlying Index Ticker', 'Dvd Freq']]

    list_stock = json.loads(ddf.to_json(orient='records'))
    collection_name = "stock_data"
    db_name = "asset_analytics"
    #req = requests.get("https://eodhistoricaldata.com/api/exchanges-list/?api_token=60241295a5b4c3.00921778&fmt=json")

    #req = requests.get("https://eodhistoricaldata.com/api/fundamentals/CAC.PA?api_token=60241295a5b4c3.00921778&fmt=json")
    #fundamental_data = req.json()

    access_db = "mongodb+srv://sngoube:Yqy8kMYRWX76oiiP@cluster0.jaxrk.mongodb.net/asset_analytics?retryWrites=true&w=majority"
    server = MongoClient(access_db)
    lstock = ddf.to_dict(orient='records')

    sdict = dict()
    for ss in lstock:
        sdict['{}.{}'.format(ss['Code'], ss['ExchangeCode'])] = ss

    # lstock = lstock[0:10]

    stock_data_list = []
    ct = 1
    total = len(lstock)
    nlstock = []
    #for sgroup in stringlist:
    for stock in lstock:
        cod = '{}.{}'.format(stock['Code'], stock['ExchangeCode'])
        print('Total loaded {}/{} - Getting data for sub string {}'.format(ct, total, cod))
        sreq = "https://eodhistoricaldata.com/api/fundamentals/{}?api_token=60241295a5b4c3.00921778&fmt=json".format(cod)
        print('sreq:{}'.format(sreq))
        req = requests.get(sreq)
        if is_valid_json(req):
            stock_data = req.json()
            stock_data['Code'] = stock['Code'] #stock_data['General']['Code']
            stock_data['Exchange'] = stock_data['General']['Exchange']
            stock_data['Type'] = stock['Type'] # sdict[cod]['Type']
            stock_data['Country'] = stock['Country'] # sdict[cod]['Country']
            stock_data['ISIN'] = stock['ISIN'] # sdict[cod]['ISIN']
            stock_data['FullCode'] = cod
            stock_data['ETF Underlying Index Ticker'] = stock['ETF Underlying Index Ticker']

            stock_data = remove_special_car(stock_data)
            stock_data_list.append(stock_data)
            stock['logo'] = ''
            if 'LogoURL' in stock_data['General'].keys():
                stock['logo'] = stock_data['General']['LogoURL']

            stock_data = add_translation(stock_data, field='Description',
                                         llg=['de', 'it', 'fr', 'es', 'nl', 'en'])
            stock_data = add_translation(stock_data, field='Category',
                                         llg=['de', 'it', 'fr', 'es', 'nl', 'en'])
            filtering = {'FullCode': cod}
            nlstock.append(stock)
            server[db_name][collection_name].find(filtering)
            server[db_name][collection_name].update_one(filtering, {'$set': stock_data}, upsert=True)
            print("load data for {} completed, with query {}!".format(cod, filtering))
        ct = ct + 1

    #from datetime import datetime
    #ds = datetime.now().strftime("%d%m%Y%H%M%S%f")
    #ddf.to_csv("./stock_universe_{}.csv".format(ds))
    #ddf2 = pd.DataFrame(nlstock)

    #ddf2 = ddf2[['ISIN', 'Code', 'Name', 'Country', 'Exchange', 'Currency', 'Type', 'ExchangeCode',
    #           'ETF Underlying Index Ticker', 'Dvd Freq','logo']]
    #ddf2.to_csv("./stock_universe.csv".format(ds))

    collection_name = "stock_universe"
    if collection_name in server[db_name].list_collection_names():
        server[db_name][collection_name].drop()
    server[db_name][collection_name].insert_many(nlstock)

    print("Done!")
    print("Disconnected!")
    server.close()


def add_translation(stock_data, field ='Category', llg = ['de', 'it', 'fr', 'es', 'nl', 'en']):
    if field in stock_data['General'].keys():
        text = stock_data['General'][field]
        ddescp = translate(text, llg)
        for lg in llg:
            stock_data['General']['{}_{}'.format(field, lg)] = ddescp[lg]
    return stock_data


def translate(text='Hello world', llg = ['de', 'it', 'fr', 'es', 'nl', 'en']):
    import requests, uuid, json

    # Add your subscription key and endpoint
    subscription_key = "f61d9d12813c4ed6ba2baa2dde83abff"
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # Add your location, also known as region. The default is global.
    # This is required if using a Cognitive Services resource.
    location = "francecentral"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '2.0',
        'from': 'en',
        'to': ['de', 'it']
    }
    constructed_url = endpoint + path

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': 'Hello World!'
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))

def translate2(text='Hello world', llg = ['de', 'it', 'fr', 'es', 'nl', 'en']):

    import requests, uuid, json
    # Add your subscription key and endpoint
    subscription_key = "f61d9d12813c4ed6ba2baa2dde83abff"
    endpoint = "https://api.cognitive.microsofttranslator.com/"

    # Add your location, also known as region. The default is global.
    # This is required if using a Cognitive Services resource.
    location = "francecentral"

    path = '/translate'

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': llg
    }
    constructed_url = endpoint + path

    headers = {
        'Ocp-Apim-Subscription-Key': 'f61d9d12813c4ed6ba2baa2dde83abff',
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': '{}'.format(text)
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    print("except :response{}".format(request.text))
    response = request.json()
    ddt = dict()
    try:
        lelt = response[0]['translations']
        for tt in lelt:
            ddt[tt['to']] = tt['text']
    except:
        ddt = dict()
        print("except :response{}".format(response))
    finally:
        print('{} , {}'.format(type(response), response))
        print("finally :ddt {}".format(ddt))
        return ddt

    print('{} , {}'.format(type(response), response))
    print('{} , {}'.format(type(ddt), ddt))
    return ddt

if __name__ == '__main__':
    #load_stock_universe()
    #load_equity_etf_list()
    #load_exchange_list()
    translate(text='Hello world', llg=['de', 'it', 'fr', 'es', 'nl', 'en'])


