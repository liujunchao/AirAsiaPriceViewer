from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

import os
from datetime import datetime, timedelta
import time

def getPrice(price):
    return price.replace(" CNY","").replace(",","");



def getCityData(db,fromCityCode,toCityCode):
    results = db.flight.find({"fromCityCode": fromCityCode,"toCityCode":toCityCode})
    data = {}
    for flightRecord in results:
        del flightRecord["_id"]
        flightPrice = getPrice(flightRecord["price"])
        flightDate = flightRecord["date"]
        if (flightDate not in data):
            data[flightDate] = {
                "price":flightPrice,
                "list": [flightRecord]
            }
        else:
            obj = data[flightDate]
            obj["list"].append(flightRecord)
            if (obj["price"] > flightPrice):
                obj["price"] = flightPrice
    return data


def getAllLocationData():
    domesticCitiesList = []
    foreignCitiesList = []

    client = MongoClient('localhost', 27017)
    db = client.location_collection
    foreignCitiesCursor = db.foreign_cities.find({})
    domesticCitiesCursor = db.china_cities.find({})
    locationDic = {}
    for city in domesticCitiesCursor:
        del city["_id"]
        domesticCitiesList.append(city)
        locationDic[city["location"]] = city["desc"]
    for city in foreignCitiesCursor:
        del city["_id"]
        foreignCitiesList.append(city)
        locationDic[city["location"]] = city["desc"]

    for city in domesticCitiesList:
        locationDic[city["location"]] = city["desc"]
    for city in foreignCitiesList:
        locationDic[city["location"]] = city["desc"]
    list = []
    for domestic in domesticCitiesList:
        for foreign in foreignCitiesList:
            list.append({
                "from":domestic["location"],
                "to":foreign["location"],
                "fromDesc": locationDic[domestic["location"]],
                "toDesc": locationDic[foreign["location"]],
                "data" : getCityData(db,domestic["location"], foreign["location"])
            })
    return {"result":list,"domesticCitiesList":domesticCitiesList,"foreignCitiesList":foreignCitiesList}
