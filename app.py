from flask import Flask, request, Response

from helper_files.helpers import parse_json, hash_string, gensalt, ObjectId
import helper_files.helpers
from ai import ai
from config import MongoDataBase

app = Flask(__name__)
app.register_blueprint(ai)

DB = MongoDataBase()
users = DB.get_collection("users")

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

    if users.find_one({'username': user['username']}):
        return Response(status=409)

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
    if hash_string(request.form['key']) == DB.delete_key:
        users.delete_many({})
        return Response(status=200)
    return Response(status=401)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
