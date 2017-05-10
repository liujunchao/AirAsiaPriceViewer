from bs4 import BeautifulSoup
import requests
import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



my_headers = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
   "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)"
]

headers = {"User-Agent": "", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}


def parseDom(scrawlDom,children):
    list = []
    idx = 0
    hasScrawlDomCls = "className" in scrawlDom
    hasScrawlDomIdx = "index" in scrawlDom
    hasScrawlDomId = "id" in scrawlDom
    for childDom in children:
        if childDom.name == scrawlDom["tagName"].lower():
            hasChildDomCls =  "class" in childDom.attrs
            hasChildDomId = "id" in childDom.attrs
            childDomClsName = None
            if hasChildDomCls:
                childDomClsName = " ".join(childDom["class"])
                if childDomClsName == "":
                    hasChildDomCls = False
            hasClsAndMatched = hasChildDomCls and hasScrawlDomCls and childDomClsName == scrawlDom["className"]
            hasIdAndMatched = hasChildDomId and hasScrawlDomId and childDom["id"] == scrawlDom["id"]
            if childDom.name == "body" or childDom.name == "html":
                list.append(childDom)
                continue
            if hasScrawlDomIdx:
                if hasClsAndMatched:
                    idx = idx + 1
                elif not hasChildDomCls and not hasScrawlDomCls:
                    idx = idx + 1
                if idx != scrawlDom["index"]:
                    continue

            if not hasScrawlDomId and not hasChildDomId and not hasChildDomCls and not hasScrawlDomCls:
                list.append(childDom)
                continue
            if not hasScrawlDomId and not hasChildDomId and hasClsAndMatched:
                list.append(childDom)
                continue
            if not hasScrawlDomCls and not hasChildDomCls and hasIdAndMatched:
                list.append(childDom)
                continue
            if hasClsAndMatched and hasIdAndMatched:
                list.append(childDom)

    return list

def loopDom(scrawlDom,matchChildren):
    while True:
        if "child" not in scrawlDom:
            return found
        else:
            scrawlDom = scrawlDom["child"]
        found = parseDom(scrawlDom, matchChildren)
        matchChildren = []
        for fndItm in found:
            for ele in fndItm.children:
                matchChildren.append(ele)



def parseHtml(url,rule):
    in_json = json.loads(rule)
    print(in_json)

    useSelenium = False
    requestText = None
    if useSelenium:
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(1)
        requestText = driver.page_source
    else:
        session = requests.Session()
        retryTimes = 0
        while True:
            try:
                headers["User-Agent"] = random.choice(my_headers)
                headers["Referer"] = url
                headers["Connection"] = "Connection:keep-alive"
                headers["Cache-Control"] = "no-cache"
                req = session.get(url, headers=headers ,timeout=None)
                requestText = req.text
                break
            except Exception as e:
                print(Exception, ":", e)
                time.sleep(5)
                retryTimes= retryTimes+1
                if retryTimes>10:
                    return
    bsObj = BeautifulSoup(requestText,"html.parser")
    scrawlDom = in_json;
    list = bsObj.find_all(scrawlDom["tagName"].lower())
    found = []
    for ele in list:
        for itm in loopDom(scrawlDom,ele.children):
            found.append(itm)
    return

    # list = []
    # for row in rows:
    #     rowOfFareLight = row.findAll("tr",{"class","fare-light-row"})
    #     if len(rowOfFareLight)>0:
    #         startHour = row.findAll("td",{"class":"avail-table-detail"})[0].getText()
    #         endHour = row.findAll("td",{"class":"avail-table-detail"})[1].getText()
    #         price = row.findAll("div",{"class":"avail-fare-price"})[0].getText()
    # return list
#list = parseHtml("http://www.csdn.net")