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
import os.path
import csv
from csv import DictWriter

def find_by_key(data, target, isDict):
    if(isDict):
        for key, value in data.items():
            if key == target:
                return value
            elif isinstance(value, dict) and bool(value):
                res = find_by_key(value, target, True)
                if bool(res):
                    return res
            elif isinstance(value, list) and bool(value):
                res = find_by_key(value, target, False)
                if bool(res):
                    return res
    else:
        for value in data:
            if isinstance(value, dict) and bool(value):
                res = find_by_key(value, target, True)
                if bool(res):
                    return res
            elif isinstance(value, list) and bool(value):
                res = find_by_key(value, target, False)
                if bool(res):
                    return res

def init_file():
    with open("./data/collections_list.csv", 'w') as collection_list_file:
        collection_list_file.truncate()
        history_header = csv.DictWriter(collection_list_file, delimiter=',', fieldnames=['page Date','Name','Link','saleStartTime','saleEndTime'])
        history_header.writeheader()
        collection_list_file.close()

def get_collections_list():

    print("----------------------------- Get Collections List -------------------------------", "\n", "\n")

    lastNames = []      # 1day ago promoLinks list
    prescraped_last_date = '20210409061037'

    # Get prescraped data from collections_list.csv 
    if os.path.isfile('./data/collections_list.csv'):
        with open('./data/collections_list.csv', 'r') as collection_list_file:
            reader = csv.DictReader(collection_list_file)
            fieldnames = reader.fieldnames
            if 'page Date' in fieldnames:
                prescraped_data= pd.read_csv("./data/collections_list.csv")
                for index in range(0, prescraped_data["page Date"].count()):
                    lastNames.append(prescraped_data["Name"][index])
                if prescraped_data["page Date"].count() > 0:
                    prescraped_last_date = max(prescraped_data["page Date"])
                collection_list_file.close()
            else:
                collection_list_file.close()
                # Init collections_list.csv file to empty and append header
                init_file()

    else:
        # Init collections_list.csv file to empty and append header
        init_file()


    # Get 6 months ago date
    nowDate = datetime.datetime.now()
    lastDate =  nowDate - relativedelta.relativedelta(months=6)
    url = 'http://web.archive.org/cdx/search/cdx?url=opensea.io&collapse=digest&from='+lastDate.strftime("%Y%m%d") + '&to=' + nowDate.strftime("%Y%m%d") + '&output=json'
    urls = rq.get(url).text
    parse_url = json.loads(urls) #parses the JSON from urls.

    ## Extracts timestamp and original columns from urls and compiles a url list.
    url_list = []
    for i in range(1,len(parse_url)):
        orig_url = parse_url[i][2]
        tstamp = parse_url[i][1]
        waylink = tstamp+'/'+orig_url
        if int(tstamp) > int(prescraped_last_date):
            url_list.append(waylink)

    for url in url_list:    # Scrap these URLs
        final_url = 'https://web.archive.org/web/'+url

        print("----------------------------- URL -------------------------------")
        print(final_url)
        print("-----------------------------------------------------------------")
        
        pageDate = final_url[28:42]     # Extract timestamp in URL
        req = rq.get(final_url).text
        soup = bs(req, 'html.parser')
        if bool(soup.find('script', attrs = {'id':'__NEXT_DATA__'})):
            collections_json_data = soup.find('script', attrs = {'id':'__NEXT_DATA__'}).string    # All collections data
        else: 
            continue
        collections_obj_data = json.loads(collections_json_data)
        json_data = find_by_key(collections_obj_data, "json", True)
        if (json_data == None):
            continue
        promotions_list = json_data['data']['promotions']
        if (promotions_list == None):
            continue
        for promotion in promotions_list:
            if promotion['promoHeader'] in lastNames:
                continue
            promoName = ''
            promoLink = ''
            promoStart = ''
            promoEnd = ''
            if promotion.__contains__('promoHeader') and bool(promotion['promoHeader']):
                promoName = promotion['promoHeader']
            if promotion.__contains__('promoCardLink') and bool(promotion['promoCardLink']):
                promoLink = promotion['promoCardLink']
            if promotion.__contains__('saleStartTime') and bool(promotion['saleStartTime']):
                promoStart = promotion['saleStartTime']
            if promotion.__contains__('saleEndTime') and bool(promotion['saleEndTime']):
                promoEnd = promotion['saleEndTime']

            print("Page Date: " + pageDate)
            print("Name: " + promoName)
            print("Link: " + promoLink)
            print("saleStartTime: " + promoStart)
            print("saleEndTime: " + promoEnd)
            print("\n")

            collection_data = {
                'page Date': pageDate,
                'Name': promoName,
                'Link': promoLink,
                'saleStartTime': promoStart,
                'saleEndTime': promoEnd
            }
            lastNames.append(promotion['promoHeader'])
            # Append new collection data to collections_list.csv
            headersCSV = ['page Date','Name','Link','saleStartTime','saleEndTime']      
            with open('./data/collections_list.csv', 'a', newline='', encoding='utf-8') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=headersCSV)
                dictwriter_object.writerow(collection_data)
                f_object.close()

if __name__ == '__main__':
    
    get_collections_list()