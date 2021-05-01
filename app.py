from flask import Flask, request, Response
import pymongo
from bson.objectid import ObjectId
from bson import json_util
import json
import hashlib
from bcrypt import gensalt

app = Flask(__name__)

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

mongod = mongo_client["users"]
users = mongod["users"]

delete_key = 'b339da421f0551238dcba7010211444ece30894857d608deb905babd047fb0f17a92e98287287138b4adac05e55351c3ee6aa71d1a4a99333a652f256e998dd9'

def parse_json(data):
    return json.loads(json_util.dumps(data))

def hash_string(password):
    return hashlib.sha512(password.encode('utf-8')).hexdigest()

@app.route('/')
def root():
    return 'hello wordl!'

@app.route('/add_user', methods=['POST'])
def create_user():
    user = {}

    salt = str(gensalt())
    password = hash_string(request.form['password'] + salt)

    user['username'] = request.form['username']
    user['password'] = password
    user['salt'] = salt
    return str(users.insert_one(user).inserted_id)

@app.route('/get_user', methods=['GET'])
def get_user():
    json_data = parse_json(
        users.find_one(
            {'_id': ObjectId(request.form['id'])}
        )
    )
    if json_data:
        return json_data
    return Response(status=401)

@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    list_of_users = {}

    for i in users.find():
        ID = i['_id']
        del i['_id']
        list_of_users[str(ID)] = i

    return list_of_users

@app.route('/login', methods=['GET'])
def login():
    user = users.find_one({'username': request.form['username']})
    
    password = hash_string(request.form['password'] + user['salt'])

    if password == user['password']:
        return Response(status=200)
    return Response(status=401)

@app.route('/clear_users', methods=['DELETE'])
def clear_users():
    if hash_string(request.form['key']) == delete_key:
        users.delete_many({})
        return Response(status=200)
    return Response(status=401)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
