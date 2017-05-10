from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

import os
from datetime import datetime, timedelta
import time

def saveFlightData(db,obj):
    db.flight.insert(obj)

client = MongoClient('chaoyiyi.cn', 27017)
db = client.location_collection

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
url = "http://www.airasia.com/cn/zh/home.page?cid=1"
# html = urlopen(url)
session = requests.Session()
index=0
while True:
    try:
        index = index+1
        print("start:"+str(index))
        req = session.get(url, headers=headers)

        bsObj = BeautifulSoup(req.text, "html.parser")
        print("fetched")
        #print(req.text);
        # for itm in bsObj.find(id='fromFlyoutBody').children:
        #     print(itm)
        # break
    except Exception as e:
        print(Exception, ":", e)
       # time.sleep(5)