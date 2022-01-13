#!/usr/bin/env python3

from __init__ import kitten
from flask import Flask, jsonify
import json
from util import  get_meta_data
import requests
import time
import os


MASTER=os.environ['MASTER']
try:
    CLONE=os.environ['CLONE']
except:
    CLONE=False

app = Flask(__name__)

@app.route('/worker/<worker_idx>', methods=['POST'])
def create_worker(worker_idx):
    kitten.set_worker_idx(int(worker_idx))
    worker = kitten.add_worker()
    #print('worker:', worker)
    if CLONE:
        os.system(f'./clone {CLONE} {worker_idx}')
    if worker is not None:
        worker = str(worker)
    return jsonify(worker)


@app.route('/put/<key>/<val>', methods=['PUT'])
def put_req(key, val):
    ret = kitten.put(key, val)

    # make the payload here; gonna be metadata
    metadata = get_meta_data(kitten.worker_idx)

    r = requests.post(f'http://localhost:{MASTER}/add_worker', json=json.dumps(metadata))
    if ret is not None:
        ret = str(ret)
    return jsonify(ret)
@app.route('/put_file/<key>/<path:path>', methods=['PUT'])
def put_file(key, path):
    infile = open(path, 'rb')
    data = infile.read()
    kitten.put(key, str(data))
    ret = 'Saved ' + path
    # make the payload here; gonna be metadata
    metadata = get_meta_data(kitten.worker_idx)
    r = requests.post(f'http://localhost:{MASTER}/add_worker', json=json.dumps(metadata))
    if ret is not None:
        ret = str(ret)
    return jsonify(ret)

@app.route('/get/<key>')
def get_req(key):
    ret = kitten.get(key)
    if ret is not None:
        ret = str(ret.decode('utf-8'))
    return jsonify(ret)

@app.route('/delete/<key>', methods=['DELETE'])
def delete_req(key):
    ret = kitten.delete(key, with_hash=False, is_testing=False)
    if ret is not None:
        ret = str(ret.decode('utf-8'))
    return jsonify(ret)

@app.route('/getindex')
def get_index():
    return jsonify(kitten.worker_idx - 1)

@app.route('/clear', methods=['DELETE'])
def clear():
    kitten.clear_worker(testing=False)
    return jsonify("Cleared worker")

@app.route('/close')
def close():
    ret = kitten.close_worker()
    return jsonify(ret)

if __name__ == "__main__":
    app.run()
