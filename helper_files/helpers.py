from bson.objectid import ObjectId
from bson import json_util
import json
import hashlib
from bcrypt import gensalt

def parse_json(data):
    return json.loads(json_util.dumps(data))

def hash_string(password):
    return hashlib.sha512(password.encode('utf-8')).hexdigest()