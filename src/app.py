from flask import Flask, request, Response

from helper_files.helpers import parse_json, hash_string, gensalt, ObjectId, decode_auth_token, encode_auth_token
import helper_files.helpers
from ai_endpoint import ai_endpoint
from blog_endpoint import blog_endpoint
from config import MongoDataBase

import os

app = Flask(__name__)
app.register_blueprint(ai_endpoint)
app.register_blueprint(blog_endpoint)

DB = MongoDataBase()
users = DB.get_collection("users")

@app.route('/')
def root():
    return 'hello wordl!'

@app.route('/add_user', methods=['POST'])
def create_user():
    user = {}

    salt = str(gensalt())
    password = hash_string(request.json['password'] + salt)

    user['username'] = request.json['username']
    user['password'] = password
    user['salt'] = salt

    if users.find_one({'username': user['username']}):
        return {}, 409

    token = encode_auth_token(users.insert_one(user).inserted_id)

    return {"token":token}, 201

@app.route('/get_user', methods=['GET'])
def get_user():
    json_data = parse_json(
        users.find_one(
            {'_id': ObjectId(request.json['id'])}
        )
    )
    if json_data:
        return json_data
    return {}, 401

@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    list_of_users = {}

    for i in users.find():
        ID = i['_id']
        del i['_id']
        list_of_users[str(ID)] = i

    return list_of_users

@app.route('/login', methods=['POST'])
def login():
    user = users.find_one({'username': request.json['username']})

    if not user:
        return {}, 401
    
    password = hash_string(request.json['password'] + user['salt'])

    if password == user['password']:
        token = encode_auth_token(user['_id'])
        print(token)
        return {"token":token}, 200
    return {}, 401

@app.route('/clear_users', methods=['DELETE'])
def clear_users():
    if hash_string(request.json['key']) == DB.delete_key:
        users.delete_many({})
        return {}, 200
    return {}, 401

@app.route('/auth_user', methods=['POST'])
def auth_user():
    _id = decode_auth_token(request.json['token'])
    if _id == ('Signature expired. Please log in again.') or _id == ('Invalid token. Please log in again.'): return {"error":_id}, 404
    user = users.find_one({'_id': ObjectId(_id)})
    if user:
        return {}, 201
    return {}, 404


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
