from pymongo import MongoClient
client = MongoClient('chaoyiyi.cn', 27017)
db = client.scrawl_collection
def saveTopic(obj):
    db.topics.insert(obj)
def findTopics():
    return db.topics.find()