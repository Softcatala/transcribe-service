#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from __future__ import print_function
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import json
from batchfilesdb import BatchFilesDB
import os
import uuid
import logging
import logging.handlers

app = Flask(__name__)

CORS(app)

MODELS = '/srv/models/'
UPLOAD_FOLDER = '/srv/data/files/'
PROCESSED_FOLDER = '/srv/data/processed/'
SAVED_TEXTS = '/srv/data/saved/'

@app.route('/hello', methods=['GET'])
def hello_word():
    return "Hello!"


def init_logging():
    logfile = 'translate-service.log'

    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logger = logging.getLogger()
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes=1024*1024, backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    logger.addHandler(console)

def _allowed_file(filename):
    ALLOWED_EXTENSIONS = ['mp3', 'wav', 'ogg', 'avi', 'mp4']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file_to_process(filename, email, model_name, original_filename):
    db = BatchFilesDB()
    db.create(filename, email, model_name, original_filename)
    
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@app.route('/get_file/', methods=['GET'])
def get_file():
    uuid = request.args.get('uuid')
    ext = request.args.get('ext')

    if uuid == '':
        result = {}
        result['error'] = "No s'ha especificat el uuid"
        return json_answer(result, 404)

    if not is_valid_uuid(uuid):
        result = {}
        result['error'] = "uuid no vàlid"
        return json_answer(result, 400)

    if ext == '':  
        result = {}
        result['error'] = "No s'ha especificat l'extensió"
        return json_answer(result, 404)

    logging.debug(f"Get file {uuid} - {ext}")
    fullname = os.path.join(PROCESSED_FOLDER, uuid)
    fullname = f"{fullname}.{ext}"

    if not os.path.exists(fullname):
        result = {}
        result['error'] = "No existeix aquest fitxer. Potser ja s'esborrat."
        return json_answer(result, 404)

    with open(fullname, mode='rb') as file:
        content = file.read()

    resp = Response(content, mimetype="application/octet-stream")
    resp.headers["Content-Length"] = len(content)
    resp.headers["Content-Disposition"] = "attachment; filename=%s" % "file." + ext
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#    return content

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@app.route('/translate_file/', methods=['POST'])
def upload_file():
    file = request.files['file'] if 'file' in request.files else ""
    email = request.values['email'] if 'email' in request.values else ""    
    model_name = request.values['model_name'] if 'model_name' in request.values else ""    

    if file == '' or file.filename == '':
        result = {}
        result['error'] = "No s'ha especificat el fitxer"
        return json_answer(result, 404)

    if email == '':
        result = {}
        result['error'] = "No s'ha especificat el correu"
        return json_answer(result, 404)
        
    if model_name == '':
        result = {}
        result['error'] = "No s'ha especificat el model"
        return json_answer(result, 404)
        
    if file and _allowed_file(file.filename):
        filename = uuid.uuid4().hex
        fullname = os.path.join(UPLOAD_FOLDER, filename)
        file.save(fullname)

        save_file_to_process(fullname, email, model_name, file.filename)
        size = os.path.getsize(fullname)
        logging.debug(f"Saved file {file.filename} to {fullname} (size: {size})")
        result = []
        return json_answer(result)

    result = {}
    result['error'] = "Error desconegut"
    return json_answer(result, 500)


def json_answer(data, status = 200):
    json_data = json.dumps(data, indent=4, separators=(',', ': '))
    resp = Response(json_data, mimetype='application/json', status = status)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':
#    app.debug = True
    init_logging()
    app.run()

if __name__ != '__main__':
    init_logging()
