from flask import Flask, request, Response, Blueprint
from flask_accept import accept

from helper_files.helpers import parse_json, hash_string
from config import MongoDataBase
from containers.ai_endpoints.train import TrainModel, sample
from keras.models import load_model

import pickle
import time
import numpy as np
import random
import os

ai = Blueprint('ai', __name__)

DB = MongoDataBase()
datasets = DB.get_collection("datasets")
models = DB.get_collection("models")

delete_key = 'b339da421f0551238dcba7010211444ece30894857d608deb905babd047fb0f17a92e98287287138b4adac05e55351c3ee6aa71d1a4a99333a652f256e998dd9'

@ai.route('/ai/', methods=['GET'])
def AI():
    return 'THIS IS AI'

@ai.route('/ai/upload_dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return Response(status=400)

    text_file = request.files['file']
    file_name = text_file.filename
    
    if file_name == '' or text_file.content_type != 'text/plain':
        return Response(status=400)

    
    if datasets.find_one({'name': file_name}):
        return Response(status=409)
    
    datasets.insert_one({'name':file_name, 'text': str(text_file.read())}).inserted_id
    return Response(status=201)


@ai.route('/ai/get_datasets', methods=['GET'])
def get_datasets():
    list_of_datasets = {}
    for i in datasets.find():
        ID = i['_id']
        del i['_id']
        del i['text']
        list_of_datasets[str(ID)] = i

    return list_of_datasets

@ai.route('/ai/clear_datasets', methods=['DELETE'])
def clear_datasets():
    if hash_string(request.form['key']) == delete_key:
        datasets.delete_many({})
        return Response(status=200)
    return Response(status=401)

@ai.route('/ai/train_dataset', methods=['POST'])
def train_datasets():
    dataset = datasets.find_one({'name':request.form['dataset']})

    if not dataset:
        return Response(status=401)

    epochs = None
    if 'epochs' in request.form:
        epochs = request.form['epochs']
    else: 
        epochs = 10

    train_dataset =  TrainModel(dataset['text'], 10)
    created_model = train_dataset.train_model()
    created_time = time.time()

    hash_name = hash_string(dataset['text']+str(created_time))

    model = {
        'hash': hash_name,
        'name': request.form['dataset'],
        'text': dataset['text'],
        'maxlen': train_dataset.maxlen,
        'epochs': epochs,
        'time': created_time
    }

    created_model.save('ai_helpers/models/'+hash_name)
    info = models.insert_one(model)

    details = {
        '_id': str(info.inserted_id),
        'hash': hash_name,
        'name': request.form['dataset'],
        'time': created_time
    }

    return details

@ai.route('/ai/get_models', methods=['GET'])
def get_models():
    list_of_models = {}
    for i in models.find():
        ID = i['_id']
        del i['_id']
        del i['text']
        list_of_models[str(ID)] = i

    return list_of_models

@ai.route('/ai/clear_models', methods=['DELETE'])
def clear_models():
    if hash_string(request.form['key']) == delete_key:
        for i in models.find():
            os.remove('ai_helpers/models/'+i['hash'])

        models.delete_many({})
        return Response(status=200)
    return Response(status=401)

@ai.route('/ai/predict', methods=['GET'])
def predict():
    length = int(request.form['length'])
    diversity = float(request.form['diversity'])

    model_info = models.find_one({'hash':request.form['hash']})

    text = model_info['text'].lower()
    chars = sorted(list(set(text)))

    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))

    text_length = len(text)
    maxlen = model_info['maxlen']
    charlen = len(chars)
    

    model = load_model('ai_helpers/models/'+request.form['hash'])

    sentence = None

    # Get random starting text
    if 'seed' in request.form:
        sentence = request.form['seed'].lower()
    else:
        start_index = random.randint(0, text_length - maxlen - 1)
        sentence = text[start_index: start_index + maxlen]

    print(sentence)
    
    generated = ''
    generated += sentence

    for _ in range(length):
            x_pred = np.zeros((1, maxlen, charlen))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char
    return generated



    

    