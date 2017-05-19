from bs4 import BeautifulSoup
import requests
import time
import json
import random
from selenium import webdriver
from business import MongodbHelper
from business import urlAnalysis


my_headers = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
   "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)"
]

headers = {"User-Agent": "", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}

elementsNotMatched = []


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
                childDomClsName = (" ".join(childDom["class"])).strip()
                if childDomClsName == "":
                    hasChildDomCls = False
            hasClsAndMatched = hasChildDomCls and hasScrawlDomCls and childDomClsName == scrawlDom["className"]
            if "rel" in scrawlDom and scrawlDom["rel"] == "sub":
                hasClsAndMatched = hasChildDomCls and hasScrawlDomCls and scrawlDom["className"] in childDomClsName
            if "rel" in scrawlDom and scrawlDom["rel"] == "sup":
                hasClsAndMatched = hasChildDomCls and hasScrawlDomCls and childDomClsName in scrawlDom["className"]
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
    found = []
    while True:
        if "child" not in scrawlDom:
            if "children" in scrawlDom:
                return loopDomChildren(scrawlDom["children"],found)
            return found
        else:
            scrawlDom = scrawlDom["child"]

        found = parseDom(scrawlDom, matchChildren)


        if found.__len__() == 0:
            elementsNotMatched =[]
            msgInfo = {}
            for eleNotMatched in matchChildren:
                if eleNotMatched == "\n":
                    continue
                if eleNotMatched.name != scrawlDom["tagName"].lower():
                    continue
                msgInfo["tagName"] = eleNotMatched.name
                if "class" in eleNotMatched.attrs:
                    msgInfo["className"] = (" ".join(eleNotMatched["class"])).strip()
                if "id" in eleNotMatched.attrs:
                    msgInfo["id"] = eleNotMatched["id"]
                elementsNotMatched.append(eleNotMatched)
            print("find nothing，got not matched elements")
        matchChildren = []
        hasRelatedTopic = "relatedTopic" in scrawlDom
        if hasRelatedTopic:
            topicRule = MongodbHelper.getTopicByObjectId(scrawlDom["relatedTopic"])
        for fndItm in found:
            if hasRelatedTopic:
                fndItm["relatedTopic"] = topicRule
            for ele in fndItm.children:
                matchChildren.append(ele)
        if found.__len__() == 0:
            scrawlDomInfo = scrawlDom["tagName"]
            if "className" in scrawlDom:
                scrawlDomInfo= " className="+scrawlDom["className"]
            if "id" in scrawlDom:
                scrawlDomInfo = " id=" + scrawlDom["id"]

            print("find nothing,scrawlDom:"+scrawlDomInfo)
            return found



def loopDomChildren(scrawlDomList,matchChildren):
    foundList = []
    for fndItm in matchChildren:
        foundResult = []
        for scrawlDom in scrawlDomList:
            newScrawlDom = {}
            newScrawlDom["child"] = scrawlDom
            foundItm = loopDom(newScrawlDom, fndItm.children)
            foundResult.append(foundItm)
        foundList.append(foundResult)
    return foundList



def getFoundHtml(url,rule,scrawlType):
    in_json = json.loads(rule)
    print(in_json)

    useSelenium = True if scrawlType == "webdriver.chrome" else False
    requestText = None
    if useSelenium:
        try:
            driver = webdriver.Chrome()
            driver.set_page_load_timeout(60)
            driver.get(url)
            # time.sleep(12)
            requestText = driver.page_source
            driver.quit()
        except Exception as e:
            print(Exception, ":", e)
            return []
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
                req.encoding = req.apparent_encoding
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
    htmlTags = bsObj.find_all(scrawlDom["tagName"].lower())

    result = loopDom(scrawlDom, htmlTags[0].children)

    allfound = []
    for itm in result:
        for content in itm.strings:
            print(content)
        jObj = convertDomToJson(itm)
        allfound.append(jObj)
    return allfound


def parseHtml(url,rule,scrawlType):
    foundHtml = getFoundHtml(url,rule,scrawlType)
    resultJson = {}
    if elementsNotMatched.__len__() != 0:
        resultJson["status"] = "failure"
        resultJson["result"] = elementsNotMatched
    else:
        resultJson["status"] = "success"
        resultJson["result"] = foundHtml

    return resultJson

def convertDomToJson(bsDom):
    if type(bsDom) == list:
        jList = []
        for subDom in bsDom:
            subDomJson = convertDomToJson(subDom)
            jList.append(subDomJson)
        return jList
    itmJson = {}
    itmJson["content"] = bsDom.text
    if bsDom.name == "a":
        itmJson["href"] = bsDom.attrs["href"]
        if "relatedTopic" in bsDom.attrs:
            relatedTopic = bsDom["relatedTopic"]
            print("fetch link content:"+ relatedTopic["topic"]+", href:"+itmJson["href"])
            newPath = urlAnalysis.getPath(relatedTopic["url"],itmJson["href"])
            itmJson["linkContent"] = getFoundHtml(newPath,relatedTopic["rule"],relatedTopic["scrawlType"])

    return itmJson

