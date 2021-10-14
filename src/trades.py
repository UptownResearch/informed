import sys
import requests as rq
from bs4 import BeautifulSoup as bs
from time import sleep
from time import time
import datetime
from dateutil import relativedelta
from random import randint
from warnings import warn
import json
import pandas as pd
from csv import DictWriter
import csv
import os.path

def getPromoSlug(promoLink):
    promoSlug = ''
    tokenId = ''
    assetContractAddr = ''
    # Case /collection/{slug_name}
    if (promoLink.find("collection/") != -1):
        promoSlug = promoLink[promoLink.find("collection/")+11:]
        if promoSlug.find('/') != -1:
            promoSlug = promoSlug[:promoSlug.find('/')]
        if promoSlug.find('?') != -1:
            promoSlug = promoSlug[:promoSlug.find('?')]
    # Case /assets/{contract_address}/{token_id}
    if (promoLink.find("assets/0x") != -1):
        url = 'https://api.opensea.io/api/v1/asset/'+promoLink[promoLink.find("assets/")+7:] 
        try:
            urls = rq.get(url, timeout=60).text
        except rq.Timeout as err:
            print("timeout error")
            print(url, '\n')

        try:
            parseUrls = json.loads(urls) #parses the JSON from urls.
        except:
            print("OpenSea Access is denied!")
            exit()

        if( parseUrls.__contains__('success') and parseUrls['success'] == False):
            print()
            # print("request faild")
        else:
            promoSlug = parseUrls['collection']['slug']
            tokenId = parseUrls['token_id']
            assetContractAddr = parseUrls['asset_contract']['address']

    return {
        'collection_slug': promoSlug,
        'token_id': tokenId,
        'asset_contract_addr': assetContractAddr
    }

def requestURL(req_url, limit):
    try:
        urls = rq.get(req_url, timeout=30).text
        return urls
    except rq.Timeout as err:
        if limit > 0:
            print("limit:", limit)
            requestURL(req_url, limit-1)
        else:
            print("timeout error")
            return {'success': False}

def init_file():
    with open("./data/trade_history.csv", 'w') as trade_history_file:
        trade_history_file.truncate()
        history_header = csv.DictWriter(trade_history_file, delimiter=',', fieldnames=['Collection','Occurrence Date','Item','Price','From','To','Trade Date'] )
        history_header.writeheader()
        trade_history_file.close()

def get_trades_list():

    print("----------------------------- Get Trades List -------------------------------", "\n", "\n")

    prescraped_last_date = '20210409061037'

    # Get prescraped data from collections_list.csv 
    if os.path.isfile('./data/trade_history.csv'):
        with open('./data/trade_history.csv', 'r') as trade_history_file:
            reader = csv.DictReader(trade_history_file)
            fieldnames = reader.fieldnames
            if 'Occurrence Date' in fieldnames:
                pre_trade_data= pd.read_csv("./data/trade_history.csv")
                if pre_trade_data["Occurrence Date"].count() > 0:
                    prescraped_last_date = max(pre_trade_data["Occurrence Date"])
                trade_history_file.close()
            else:
                trade_history_file.close()
                # Init collections_list.csv file to empty and append header
                init_file()

    else:
        # Init trade_history.csv file to empty and append header
        init_file()

    collections_data= pd.read_csv("./data/collections_list.csv")

    for index in range(0, collections_data["page Date"].count()):
        promoDate = str(collections_data["page Date"][index])
        # Check if trade information is already exists in csv file 
        if int(promoDate) <= int(prescraped_last_date):
            continue

        promoLink = collections_data["Link"][index]
        dropDate = datetime.datetime(int(promoDate[:4]), int(promoDate[4:6]), int(promoDate[6:8]), int(promoDate[8:10]), int(promoDate[10:12]), int(promoDate[12:] ))
        # Get collection slug name
        slugInfo = getPromoSlug(promoLink)
        promoSlug = slugInfo['collection_slug']
        tokenId = slugInfo['token_id']
        contractAddr = slugInfo['asset_contract_addr']

        if promoSlug == '' and tokenId == '':
            continue 
        if tokenId == '':
            url = 'https://api.opensea.io/api/v1/events?occurred_before='+ str((dropDate-datetime.timedelta(hours = 7)).timestamp()) + \
                    '&offset=0&limit=300&event_type=successful&collection_slug=' + promoSlug
        else:
            url = 'https://api.opensea.io/api/v1/events?occurred_before='+ str((dropDate-datetime.timedelta(hours = 7)).timestamp()) + \
                    '&offset=0&limit=300&event_type=successful&collection_slug=' + promoSlug + '&asset_contract_address=' + contractAddr + '&token_id=' + tokenId

        try:
            urls = rq.get(url, timeout=60).text
        except rq.Timeout as err:
            print("timeout error")


        try:
            parseUrls = json.loads(urls) #parses the JSON from urls.
        except:
            print("OpenSea Access is denied!")
            exit()

        if( parseUrls.__contains__('success') and parseUrls['success'] == False):
            continue
        if not bool(parseUrls['asset_events']):
            continue

        trade_info_list = parseUrls['asset_events']
        for idx, trade_info in enumerate(trade_info_list):
            # Check trade information is null
            if bool(trade_info["asset"]) == False:
                continue
            # Check blockchain is etherum
            if bool(trade_info["payment_token"]) == False:
                continue
            
            # trade_assest = find_by_key(parse_url, "asset", True)
            if idx == 0:
                trade_collection_name = trade_info["asset"]["collection"]["name"]
                trade_collection_occur = promoDate
                print("----------------------------- Collection -------------------------------")
                print(trade_collection_name, '----------', trade_collection_occur)
                print("------------------------------------------------------------------------")
            else:
                trade_collection_name = ""
                trade_collection_occur = ""


            # Get trade Item(NFT) name. If value is null, set as collection_name
            if not bool(trade_info["asset"]["name"]):
                trade_item = trade_info["asset"]["collection"]["name"]
            else:
                trade_item = trade_info["asset"]["name"]

            trade_price = int(trade_info["total_price"])/(10 ** 18)
            trade_quantity = trade_info["quantity"]

            if bool(trade_info["seller"]) and bool(trade_info["seller"]["user"]) and trade_info["seller"]["user"].__contains__("username") and bool(trade_info["seller"]["user"]["username"]):
                trade_seller_name = trade_info["seller"]["user"]["username"]
            else:
                trade_seller_name = ""        
            if not bool(trade_info["seller"]):
                trade_seller_addr = ""
            else:
                trade_seller_addr = trade_info["seller"]["address"]

            if bool(trade_info["winner_account"]["user"]) and  trade_info["winner_account"]["user"].__contains__("username") and bool(trade_info["winner_account"]["user"]["username"]):
                trade_owner_name = trade_info["winner_account"]["user"]["username"]
            else:
                trade_owner_name = ""
            if not bool(trade_info["winner_account"]):
                trade_owner_addr = ""
            else:
                trade_owner_addr = trade_info["winner_account"]["address"]
                
            trade_date = trade_info["created_date"]

            trade_history_data = {
                'Collection': trade_collection_name,
                'Occurrence Date': trade_collection_occur,
                'Item': trade_item,
                'Price': trade_price,
                'From': trade_seller_name+'('+ trade_seller_addr +')',
                'To': trade_owner_name+'('+ trade_owner_addr +')',
                'Trade Date': trade_date
            }

            headersCSV = ['Collection','Occurrence Date','Item','Price','From','To','Trade Date']      
            with open('./data/trade_history.csv', 'a', newline='', encoding='utf-8') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=headersCSV)
                dictwriter_object.writerow(trade_history_data)
                f_object.close()

if __name__ == '__main__':
    
    get_trades_list()