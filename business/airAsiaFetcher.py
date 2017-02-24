from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

import os
from datetime import datetime, timedelta
import time


def trimString(val):
    return val.lstrip('\r\n ').rstrip('\r\n ')
def trimVal(val):
    return trimString(val).lstrip('\n').rstrip('\n').replace("\n"," ");


def saveScrawRecord(db,fromCityCode,toCityCode,searchDate):
    db.fetch_indicator.update({"fromCityCode":fromCityCode,"toCityCode":toCityCode},{"$set":{
        "searchDate":searchDate
    }})


def saveFlightData(db,obj):
    db.flight.insert(obj)


def getInitDate():
    searchDate = datetime.now()
    return searchDate + timedelta(30)


def queryScrawRecordDate(db,fromCityCode,toCityCode):
    results = db.fetch_indicator.find({"fromCityCode":fromCityCode,"toCityCode":toCityCode})
    if results.count() == 0:
        searchDate = getInitDate()
        db.fetch_indicator.insert({"fromCityCode":fromCityCode,"toCityCode":toCityCode,"searchDate":searchDate})
        return searchDate
    else:
        for record in results:
            return record["searchDate"]


def parseAirAsiaHtml(text):
    bsObj = BeautifulSoup(text,"html.parser")
    rows = bsObj.findAll("tr", {"class": "fare-light-row"})
    list = []
    for row in rows:
        rowOfFareLight = row.findAll("tr",{"class","fare-light-row"})
        if len(rowOfFareLight)>0:
            startHour = row.findAll("td",{"class":"avail-table-detail"})[0].getText()
            endHour = row.findAll("td",{"class":"avail-table-detail"})[1].getText()
            price = row.findAll("div",{"class":"avail-fare-price"})[0].getText()
            list.append({
                "startHour":trimVal(startHour),
                "endHour":trimVal(endHour),
                "price":trimVal(price)
            })
    return list



pages=[]
domesticCitiesList = []
foreignCitiesList = []

client = MongoClient('localhost', 27017)
db = client.location_collection
cities1 = db.foreign_cities.find({})
cities2 = db.china_cities.find({})
for city in cities1:
    foreignCitiesList.append(city)
for city in cities2:
    domesticCitiesList.append(city)

targetDate = datetime.now()+ timedelta(170)
targetDate = datetime.strptime(targetDate.strftime('%Y-%m-%d'), '%Y-%m-%d')
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
for chinaCity in domesticCitiesList:
    for foreignCity in foreignCitiesList:
        fromCityCode = chinaCity["location"]
        toCityCode = foreignCity["location"]
        future = queryScrawRecordDate(db,fromCityCode,toCityCode)
        future = future + timedelta(1)
        while targetDate>future :
            url = "https://booking.airasia.com/Flight/Select?o1="+fromCityCode+"&d1="+toCityCode+"&culture=zh-CN&dd1=" + future.strftime("%Y-%m-%d") + "&ADT=1&CHD=0&inl=0&s=true&mon=true&cc=CNY&c=false"
            # html = urlopen(url)
            session = requests.Session()
            while True:
                try:
                    req = session.get(url, headers=headers)
                    break
                except Exception as e:
                    print(Exception, ":", e)
                    time.sleep(5)

            list = parseAirAsiaHtml(req.text)
            if list is not None:
                for obj in list:
                    obj["date"] = future.strftime("%Y-%m-%d")
                    obj["fromCityCode"] = fromCityCode
                    obj["toCityCode"] = toCityCode
                    saveFlightData(db,obj)
            saveScrawRecord(db, fromCityCode, toCityCode,future)
            print("fetch " , url)
            future = future + timedelta(1)
            time.sleep(1)