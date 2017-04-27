from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

import os
from datetime import datetime, timedelta
import time

# html = urlopen(url)
html = "<html><head><title>my title</title></head><body><ul id='myul' class='ulclass  cls2 cls3' data='ulData'><li>test</li><li>test</li></ul></body></html>"

bsObj = BeautifulSoup(html, "html.parser")

ul = bsObj.find(id='myul') #通过ID获取UL
for itm in ul.children:
    print(itm)#此处输出<li>test</li>
li_strs = bsObj.find_all(string="test") #find是查找单个，find_all是查找全部，string表示标签中的内容
for li_str in li_strs:
    print(li_str)#此处输出test
parents = li_strs[0].find_parents()  #find_parent返回上一个父节点，find_parents返回所有的父节点
next_siblings = li_strs[0].find_next_siblings()#接下来返回所有的兄弟
next_sibling = li_strs[0].find_next_sibling()#下一个兄弟
for clsName in ul["class"]:
    print(clsName) #ul["class"]返回list节点，里面放了所有的class
print("Ul id:"+ul["id"])    #id
print("Ul data:"+ul["data"])  #ulData

#以下通过soup.tagname就可以获取tag元素, tag.name可以直接获取标记名,tag.text直接可以获取标记文本。
head = bsObj.head
print("head name and title:"+head.name+"  "+head.title)  #ulData
title = bsObj.title
body = bsObj.body
ul = bsObj.ul
print("old attr:"+ul.attrs["data"])   #attrs方法返回一个dict,注意其中class的value是list
ul["data"] = "abc"        #通过这种方式修改属性值
print("new attr:"+ul.attrs["data"])
ullist = bsObj.find_all("ul")   #通过tagName找到
