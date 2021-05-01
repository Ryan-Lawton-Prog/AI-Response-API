from flask import Flask, request
import pymongo
from bson.objectid import ObjectId
from bson import json_util
import json

app = Flask(__name__)

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

mongod = mongo_client["users"]
users = mongod["users"]

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/')
def root():
    return 'hello wordl!'

@app.route('/add_user', methods=['POST'])
def create_user():
    user = {}
    user['username'] = request.form['username']
    user['password'] = request.form['password']
    return str(users.insert_one(user).inserted_id)

@app.route('/get_user', methods=['GET'])
def get_user():
    return parse_json(
        users.find_one(
            {'_id': ObjectId(request.form['id'])}
        )
    )

@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    list_of_users = {}

    for i in users.find():
        ID = i['_id']
        del i['_id']
        list_of_users[str(ID)] = i

    return list_of_users


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
