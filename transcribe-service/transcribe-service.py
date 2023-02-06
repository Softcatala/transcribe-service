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
from usage import Usage
import datetime

app = Flask(__name__)

CORS(app)

UPLOAD_FOLDER = '/srv/data/files/'
PROCESSED_FOLDER = '/srv/data/processed/'

@app.route('/hello', methods=['GET'])
def hello_word():
    return "Hello!"

@app.route('/stats/', methods=['GET'])
def stats():
    requested = request.args.get('date')
    date_requested = datetime.datetime.strptime(requested, '%Y-%m-%d')
    usage = Usage()
    result = usage.get_stats(date_requested)

    return json_answer(result)


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

@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@app.route('/uuid_exists/', methods=['GET'])
def uuid_exists():
    uuid = request.args.get('uuid')

    if uuid == '':
        result = {}
        result['error'] = "No s'ha especificat el uuid"
        return json_answer(result, 404)

    processedFiles = ProcessedFiles(uuid)
    if not processedFiles.is_valid_uuid():
        result = {}
        result['error'] = "uuid no vàlid"
        return json_answer(result, 400)

    exists, result_msg = processedFiles.do_files_exists()
    result_code = 200 if exists else 404
    logging.debug(f"uuid_exists for {uuid} - {result_code}")
    return json_answer(result_msg, result_code)


ALLOWED_MIMEYPES = {"mp3": "audio/mpeg",
                    "wav": "audio/wav",
                    "ogg": "application/ogg",
                    "flac": "audio/flac",
                    "avi": "video/x-msvideo",
                    "mp4": "video/mp4",
                    "mkv": "video/x-matroska",
                    "mov": "video/quicktime",
}

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_MIMEYPES.keys()

def _get_mimetype(extension):

    mimetype = ALLOWED_MIMEYPES.get(extension)

    if not mimetype:
        if extension == "txt":
            mimetype = "text/plain"
        else:
            mimetype = "application/octet-stream"

    return mimetype
    
def _get_record(_uuid):
    processed_dir = ProcessedFiles.get_processed_directory()
    db = BatchFilesDB(processed_dir)
    return db._read_record_from_uuid(_uuid)

@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@app.route('/get_file/', methods=['GET'])
def get_file():
    uuid = request.args.get('uuid')
    ext = request.args.get('ext')

    if ext == '':
        result = {}
        result['error'] = "No s'ha especificat l'extensió"
        logging.debug(f"/get_file/ {result['error']}")
        return json_answer(result, 404)

    if uuid == '':
        result = {}
        result['error'] = "No s'ha especificat el uuid"
        logging.debug(f"/get_file/ {result['error']}")
        return json_answer(result, 404)

    processedFiles = ProcessedFiles(uuid)
    if not processedFiles.is_valid_uuid():
        result = {}
        result['error'] = "uuid no vàlid"
        logging.debug(f"/get_file/ {result['error']}")
        return json_answer(result, 400)

    exists, _ = processedFiles.do_files_exists()
    if not exists:
        result = {"error": "uuid no existeix"}
        logging.debug(f"/get_file/ {result['error']}")
        return json_answer(result, 404)
        
    record = _get_record(uuid)
    original_name, original_ext = os.path.splitext(record.original_filename)

    if ext == "bin":
        ext = original_ext[1:]
    
    fullname = os.path.join(PROCESSED_FOLDER, uuid)
    fullname = f"{fullname}.{ext}"

    if not os.path.exists(fullname):
        result = {}
        result['error'] = "No existeix aquest fitxer. Potser ja s'esborrat."
        return json_answer(result, 404)

    with open(fullname, mode='rb') as file:
        content = file.read()

    original_name = original_name.encode("ascii", "ignore").decode("ascii")
    resp_filename = f"{original_name}.{ext}"
    mime_type = _get_mimetype(ext)
    resp = Response(content, mimetype=mime_type)
    resp.headers["Content-Length"] = len(content)
    resp.headers["Content-Disposition"] = f"attachment; filename={resp_filename}"
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Accept-Ranges'] = 'bytes'
    logging.debug(f"Send file {uuid}, ext: {ext}, mimetype: {mime_type} filename: {resp_filename}")
    Usage().log("get_file")
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
        logging.debug(f"/transcribe_file/ {result['error']} - {email}")
        return json_answer(result, 429)

    MAX_PER_EMAIL = 3
    if len(db.select(email = email)) >= MAX_PER_EMAIL:
        result = {"error": f"Ja tens {MAX_PER_EMAIL} fitxers a la cua. Espera't que es processin per enviar-ne de nous."}
        logging.debug(f"/transcribe_file/ {result['error']} - {email}")
        return json_answer(result, 429)

    _uuid = db.get_new_uuid()
    fullname = os.path.join(UPLOAD_FOLDER, _uuid)
    file.save(fullname)
    db.create(fullname, email, model_name, file.filename, record_uuid=_uuid)

    size_mb = os.path.getsize(fullname) / 1024 / 1024
    waiting_time = db.estimated_queue_waiting_time()
    logging.debug(f"Saved file {file.filename} to {fullname} (size: {size_mb:.2f}MB), waiting time: {waiting_time}")
    Usage().log("transcribe_file")
    result = {"waiting_time": str(waiting_time)}
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
