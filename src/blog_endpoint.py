from flask import Flask, request, Response, Blueprint
from flask_accept import accept

from helper_files.helpers import parse_json, hash_string
from config import MongoDataBase
import time

blog_endpoint = Blueprint('blog_endpoint', __name__)

DB = MongoDataBase()
blogs = DB.get_collection("blogs")
comments = DB.get_collection("comments")

delete_key = 'b339da421f0551238dcba7010211444ece30894857d608deb905babd047fb0f17a92e98287287138b4adac05e55351c3ee6aa71d1a4a99333a652f256e998dd9'

@blog_endpoint.route('/blog/', methods=['GET'])
def BLOG():
    return 'blog root, ignore'

@blog_endpoint.route('/blog/get_blogs', methods=['GET'])
def get_blogs():
    list_of_blogs = {}

    for i in blogs.find():
        ID = i['_id']
        del i['_id']
        list_of_blogs[str(ID)] = i

    return list_of_blogs, 201

@blog_endpoint.route('/blog/add_blog', methods=['POST'])
def add_blog():
    blog = {}
    blog['title'] = request.json['title']
    blog['subtitle'] = request.json['subtitle']
    blog['author'] = request.json['author']
    blog['date'] = time.time()
    blog['body'] = request.json['body']
    print(blog)

    _id = str(blogs.insert_one(blog))
    print(_id)
    return {'_id':_id}, 201