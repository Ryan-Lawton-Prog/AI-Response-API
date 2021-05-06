from bson.objectid import ObjectId
from bson import json_util
import json
import hashlib
from bcrypt import gensalt
import os
import jwt
import datetime

SECRET_KEY = os.getenv('SECRET_KEY', 'special_key')

def parse_json(data):
    return json.loads(json_util.dumps(data))

def hash_string(password):
    return hashlib.sha512(password.encode('utf-8')).hexdigest()

@staticmethod
def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, SECRET_KEY)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
            'iat': datetime.datetime.utcnow(),
            'sub': str(user_id)
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e