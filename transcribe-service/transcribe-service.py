#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2022-2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from processedfiles import ProcessedFiles
import os
import logging
import logging.handlers
import uuid

app = Flask(__name__)

CORS(app)

UPLOAD_FOLDER = '/srv/data/files/'
PROCESSED_FOLDER = '/srv/data/processed/'

@app.route('/hello', methods=['GET'])
def hello_word():
    return "Hello!"


def init_logging():
    LOGDIR = os.environ.get('LOGDIR', '')
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logger = logging.getLogger()
    logfile = os.path.join(LOGDIR, 'transcribe-service.log')
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes=1024*1024, backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    logger.addHandler(console)

ALLOWED_EXTENSIONS = ['mp3', 'wav', 'ogg', 'avi', 'mp4', "mkv", "mov"]
def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file_to_process(filename, email, model_name, original_filename):
    db = BatchFilesDB()
    db.create(filename, email, model_name, original_filename)

@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@app.route('/uuid_exists/', methods=['GET'])
def uuid_exists():
    uuid = request.args.get('uuid')

    if uuid == '':
        result = {}
        result['error'] = "No s'ha especificat el uuid"
        return json_answer(result, 404)

    if not ProcessedFiles(uuid).is_valid_uuid():
        result = {}
        result['error'] = "uuid no vàlid"
        return json_answer(result, 400)

    extensions = ["txt", "srt"]
    result_msg = []
    result_code = 200
    for extension in extensions:
        fullname = os.path.join(PROCESSED_FOLDER, uuid)
        fullname = f"{fullname}.{extension}"

        if not os.path.exists(fullname):
            result_msg = {"error": f"file {extension} does not exist"}
            result_code = 404
            break

    logging.debug(f"uuid_exists for {uuid} - {result_code}")
    return json_answer(result_msg, result_code)
    
def _get_mimetype(extension):

    if extension == "mp3":
        mimetype = "audio/mpeg"
    elif extension == "wav":
        mimetype = "audio/wav"
    elif extension == "ogg":
        mimetype = "application/ogg"
    elif extension == "avi":
        mimetype = "video/x-msvideo"
    elif extension == "mp4":
        mimetype = "video/mp4"
    elif extension == "mkv":
        mimetype = "video/x-matroska"
    elif extension == "mov":
        mimetype = "video/quicktime"
    elif extension == "txt":
        mimetype = "text/plain"
    else:
        mimetype = "application/octet-stream"

    logging.debug(f"_get_mimetype {extension} -> mime: {mimetype}")
    return mimetype

@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@app.route('/get_file/', methods=['GET'])
def get_file():
    uuid = request.args.get('uuid')
    ext = request.args.get('ext')

    if uuid == '':
        result = {}
        result['error'] = "No s'ha especificat el uuid"
        return json_answer(result, 404)

    processedFiles = ProcessedFiles(uuid)
    if not processedFiles.is_valid_uuid():
        result = {}
        result['error'] = "uuid no vàlid"
        return json_answer(result, 400)

    if ext == '':
        result = {}
        result['error'] = "No s'ha especificat l'extensió"
        return json_answer(result, 404)

    if ext == "bin":
        fullname, ext = processedFiles.get_binary(ALLOWED_EXTENSIONS)
    else:
        fullname = os.path.join(PROCESSED_FOLDER, uuid)
        fullname = f"{fullname}.{ext}"

    if not os.path.exists(fullname):
        result = {}
        result['error'] = "No existeix aquest fitxer. Potser ja s'esborrat."
        return json_answer(result, 404)

    with open(fullname, mode='rb') as file:
        content = file.read()

    logging.debug(f"Send file {uuid} - {ext}")

    resp = Response(content, mimetype=_get_mimetype(ext))
    resp.headers["Content-Length"] = len(content)
    resp.headers["Content-Disposition"] = "attachment; filename=%s" % "file." + ext
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@app.route('/transcribe_file/', methods=['POST'])
def upload_file():
    file = request.files['file'] if 'file' in request.files else ""
    email = request.values['email'] if 'email' in request.values else ""
    model_name = request.values['model_name'] if 'model_name' in request.values else ""

    if file == "" or file.filename == "":
        result = {"error": "No s'ha especificat el fitxer"}
        return json_answer(result, 404)

    if email == "":
        result = {"error": "No s'ha especificat el correu"}
        return json_answer(result, 404)
        
    if model_name == "":
        result = {"error": "No s'ha especificat el model"}
        return json_answer(result, 404)

    if not _allowed_file(file.filename):
        result = {"error": "Tipus de fitxer no vàlid"}
        return json_answer(result, 415)

    MAX_SIZE = 1024*1024*1024 # 1GB
    if request.content_length and request.content_length > MAX_SIZE:
        result = {"error": "El fitxer és massa gran"}
        return json_answer(result, 413)

    db = BatchFilesDB()
    if db.count() > 20:
        result = {"error": "Hi ha massa fitxers a la cua de processament. Prova-ho en una estona"}
        return json_answer(result, 429)

    db = BatchFilesDB()
    MAX_PER_EMAIL = 3
    if len(db.select(email = email)) >= MAX_PER_EMAIL:
        result = {"error": f"Ja tens {MAX_PER_EMAIL} fitxers a la cua. Espera't a que es processin per enviar-ne de nous."}
        return json_answer(result, 429)

    filename = uuid.uuid4().hex
    fullname = os.path.join(UPLOAD_FOLDER, filename)
    file.save(fullname)

    save_file_to_process(fullname, email, model_name, file.filename)
    size = os.path.getsize(fullname)
    logging.debug(f"Saved file {file.filename} to {fullname} (size: {size})")
    result = []
    return json_answer(result)

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
