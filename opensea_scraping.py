import sys
import requests as rq
from bs4 import BeautifulSoup as bs
from time import sleep
from time import time
from random import randint
from warnings import warn
import json
import pandas as pd

url = 'http://web.archive.org/cdx/search/cdx?url=opensea.io&collapse=digest&from=20210601&to=20210704&output=json'

urls = rq.get(url).text
parse_url = json.loads(urls) #parses the JSON from urls.

## Extracts timestamp and original columns from urls and compiles a url list.
url_list = []
for i in range(1,len(parse_url)):
    orig_url = parse_url[i][2]
    tstamp = parse_url[i][1]
    waylink = tstamp+'/'+orig_url
    url_list.append(waylink)

data = []   # Results

for url in url_list:    # Scrap these URLs
    final_url = 'https://web.archive.org/web/'+url

    print("----------------------------- URL -------------------------------")
    print(final_url)
    print("-----------------------------------------------------------------")
    
    pageDate = final_url[28:42]     # Extract timestamp in URL
    req = rq.get(final_url).text
    soup = bs(req, 'html.parser')
    script_tag = soup.find_all('script')    # All script tags
    if(len(script_tag) < 5):                # If number of script tag is less than 5
        continue

    script_content = soup.find_all('script')[5].text    # fifth script tag is target
    print(script_content)
    if(script_content[:16] != "window.__wired__"):      # 16 letters are compared
        continue

    print("-----------HTML PARSER--------------")
    
    json_string = soup.find_all('script')[5].text[17:]      # Remove "window.__wired__="
    stud_obj = json.loads(json_string)      # Convert string to json object

    for i in stud_obj["records"]:
        for j in stud_obj["records"][i]:
            if(j == "promoHeader"):
                print("Page Date: " + pageDate)
                print("Name: " + stud_obj["records"][i]["promoHeader"])
                print("Link: " + stud_obj["records"][i]["promoCardLink"])
                print("saleStartTime: " + stud_obj["records"][i]["saleStartTime"])
                print("saleEndTime" + stud_obj["records"][i]["saleEndTime"])
                print("\n")

                data.append({
                    'page Date': pageDate,
                    'Name': stud_obj["records"][i]["promoHeader"],
                    'Link': stud_obj["records"][i]["promoCardLink"],
                    'saleStartTime': stud_obj["records"][i]["saleStartTime"],
                    'saleEndTime': stud_obj["records"][i]["saleEndTime"]
                }) 
df = pd.DataFrame(data)
df.to_csv('nft.csv', index=False)