from flask import Flask, request, Response, Blueprint
from flask_accept import accept

from helper_files.helpers import parse_json, hash_string
from config import MongoDataBase

blog_endpoint = Blueprint('blog_endpoint', __name__)

DB = MongoDataBase()
datasets = DB.get_collection("blogs")
datasets = DB.get_collection("comments")

delete_key = 'b339da421f0551238dcba7010211444ece30894857d608deb905babd047fb0f17a92e98287287138b4adac05e55351c3ee6aa71d1a4a99333a652f256e998dd9'

@blog_endpoint.route('/blog/', methods=['GET'])
def BLOG():
    return 'blog root, ignore'

    