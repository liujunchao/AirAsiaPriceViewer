from flask import Flask,jsonify,abort,make_response,request
from DataHandler import getAllLocationData
from business import fetcher
from business import MongodbHelper
app = Flask(__name__)
import json

@app.route('/')
def hello_world():
    return 'Hello World!'


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    task = task.__next__()
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    task = task.__next__()
    if len(task) == 0:
        abort(404)
    tasks.remove(task)
    return jsonify({'result': True})

@app.route('/airasia/api/flights', methods=['GET'])
def get_flights():
    list = getAllLocationData()
    #list = json.dumps(list)
    return jsonify(list)

@app.route('/api/scrawl', methods=['POST'])
def scrawl():
    rule  = request.form["rule"]
    url = request.form["url"]
    obj = fetcher.parseHtml(url,rule)
    return jsonify(obj)

@app.route('/api/saveTopic', methods=['POST'])
def saveTopic():
    try:
        obj  = {}
        obj["url"] = request.form["url"]
        obj["rule"] = request.form["rule"]
        obj["topic"] = request.form["topic"]
        obj["scrawlType"] = request.form["scrawlType"]
        MongodbHelper.saveTopic(obj)
    except Exception:
        return jsonify({
            "status": "failure",
            "message":Exception
        })
    return jsonify({
        "status":"success"
    })


@app.route('/api/findTopics', methods=['POST'])
def findTopics():
    topics = []
    list =  MongodbHelper.findTopics()
    for record in list:
        record["_id"] = str(record["_id"])
        topics.append(record)
    return jsonify({
        "status":"success",
        "data":topics
    })


if __name__ == '__main__':
    app.run()
