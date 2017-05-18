from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient('chaoyiyi.cn', 27017)
db = client.scrawl_collection
def saveTopic(obj):
    db.topics.insert(obj)
def findTopics():
    return db.topics.find()
def getTopicByObjectId(id):
    results = db.topics.find({"_id": ObjectId(id)})
    for obj in results:
        return obj