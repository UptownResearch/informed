import sys
from numpy import NaN, nan
import requests as rq
from bs4 import BeautifulSoup as bs
from time import sleep
from time import time
from datetime import datetime
from dateutil import relativedelta
from random import randint
from warnings import warn
import json
import pandas as pd
from csv import DictWriter
import csv
import math


def get_buyer_list():

    print("----------------------------- Get Buyers List -------------------------------", "\n", "\n")

    with open("./data/buyer_list.csv", 'w') as buyer_list_file:
        buyer_list_file.truncate()
        list_header = csv.DictWriter(buyer_list_file, delimiter=',', fieldnames=['Buyer Address','Buyer Name','Trade Count','Trade Collection','Trade NFT','Trade Price','Trade Date','Featured Date'])
        list_header.writeheader()
        buyer_list_file.close()


    trade_data= pd.read_csv("./data/trade_history.csv")
    buyers_dict = {}
    # Collection and Occurrence Date field in trade_history.csv
    featured_date = ''
    collection = ''
    for index in range(0, trade_data["To"].count()):
        trade_buyer_info = trade_data["To"][index]
        print(index, trade_data["To"][index])
        buyer_name = trade_buyer_info[:trade_buyer_info.find("(")]
        buyer_addr = trade_buyer_info[(trade_buyer_info.find("(")+1):trade_buyer_info.find(")")]
        if not math.isnan(trade_data["Occurrence Date"][index]):
            featured_date = str(int(trade_data["Occurrence Date"][index]))
        if type(trade_data["Collection"][index]) == str:
            collection = trade_data["Collection"][index]
        dropDate = datetime(int(featured_date[:4]), int(featured_date[4:6]), int(featured_date[6:8]), int(featured_date[8:10]), int(featured_date[10:12]), int(featured_date[12:] ))

        buyer_trade_info = {
            'Collection': collection,
            'Item':    trade_data["Item"][index],
            'Price':   trade_data["Price"][index],
            'Date':    trade_data["Trade Date"][index],
            'Feature': dropDate.strftime("%Y-%m-%dT%H:%M:%S")
        }
        if(not buyers_dict.__contains__(buyer_addr)):
            buyers_dict[buyer_addr] = {}
            buyers_dict[buyer_addr]["transactions"] = []
            buyers_dict[buyer_addr]["trade_count"] = 0
            buyers_dict[buyer_addr]["name"] = buyer_name
            buyers_dict[buyer_addr]["address"] = buyer_addr
        buyers_dict[buyer_addr]["transactions"].append(buyer_trade_info)
        buyers_dict[buyer_addr]["trade_count"] += 1

    buyers_list = list(buyers_dict.values())    # Convert Buyer Dict to List so Sort easily

    buyers_sort_list = sorted(buyers_list, key=lambda buyer: buyer['trade_count'], reverse = True)


    for buyer_info in buyers_sort_list:
        for idx, transaction in enumerate(buyer_info["transactions"]):
            if idx == 0:
                buyerAddr = buyer_info["address"]
                buyerName = buyer_info["name"]
                buyerTradeCount = buyer_info["trade_count"]
            else:
                buyerAddr = ''
                buyerName = ''
                buyerTradeCount = ''
            buyerTradeCollection = transaction["Collection"]
            buyerTradeItem = transaction["Item"]
            buyerTradePrice = transaction["Price"]
            buyerTradeDate = transaction["Date"]
            buyerFeaturedDate = transaction["Feature"]

            ['Buyer Address','Buyer Name','Trade Count','Trade Collection','Trade NFT','Trade Price','Trade Date','Featured Date']

            buyer_data = {
                'Buyer Address': buyerAddr,
                'Buyer Name': buyerName,
                'Trade Count': buyerTradeCount,
                'Trade Collection': buyerTradeCollection,
                'Trade NFT': buyerTradeItem,
                'Trade Price': buyerTradePrice,
                'Trade Date': buyerTradeDate,
                'Featured Date': buyerFeaturedDate
            }

            headersCSV = ['Buyer Address','Buyer Name','Trade Count','Trade Collection','Trade NFT','Trade Price','Trade Date','Featured Date']   
            with open('./data/buyer_list.csv', 'a', newline='', encoding='utf-8') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=headersCSV)
                dictwriter_object.writerow(buyer_data)
                f_object.close()



if __name__ == '__main__':
    get_buyer_list()




