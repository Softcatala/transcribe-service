#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020-2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import time
import logging
import logging.handlers
import os
from batchfilesdb import BatchFilesDB
from processedfiles import ProcessedFiles
from sendmail import Sendmail
from execution import Execution, Command
import datetime
import tempfile

def init_logging():

    LOGDIR = os.environ.get('LOGDIR', '')
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logfile = os.path.join(LOGDIR, 'process-batch.log')
    logger = logging.getLogger()
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes=1024*1024, backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

def _get_extension(original_filename):
    split_tup = os.path.splitext(original_filename)

    file_extension = split_tup[1]
    if file_extension == "":
        file_extension = ".bin"

    return file_extension

def _get_model_file(model_name):
    if model_name == "small":
        model = "ggml-small.bin"
    elif model_name == "medium":
        model = "ggml-medium.bin"
    elif model_name == "sc-small":
        model = "ggml-sc-small.bin"
    elif model_name == "sc-medium":
        model = "ggml-sc-medium.bin"
    else: # default
        model = "ggml-small.bin"

    return model

def _get_threads():
    return os.environ.get('THREADS', 4)

def _get_timeout():
    return os.environ.get('TIMEOUT_CMD', 90 * 60)

def _send_mail(batchfile, inference_time, source_file_base):
    text = f"Ja tenim el vostre fitxer '{batchfile.original_filename}' transcrit amb el model '{batchfile.model_name}'. El podeu baixar des de "
    text += f"https://www.softcatala.org/transcripcio/resultats/?uuid={source_file_base}"

    if "@softcatala" in batchfile.email:
        THREADS = _get_threads()
        text += f"\nL'execució ha trigat {inference_time} amb {THREADS} threads."

    Sendmail().send(text, batchfile.email)

def _send_mail_error(batchfile, inference_time, source_file_base, message):
    text = f"No hem pogut processar el vostre fitxer '{batchfile.original_filename}' transcrit amb el model '{batchfile.model_name}'. "
    text += message

    logging.debug(f"_send_mail_error: {message} to {batchfile.email}")
    Sendmail().send(text, batchfile.email)

def main():

    print("Process batch files to transcribe")
    init_logging()
    db = BatchFilesDB()
    ProcessedFiles.ensure_dir()
    purge_last_time = time.time()
    PURGE_INTERVAL_SECONDS = 60 * 6 * 24 # For times per day
    PURGE_OLDER_THAN_DAYS = 3
    WAV_FILE = "file.wav"
    execution = Execution(_get_threads())

    temp_dir = tempfile.TemporaryDirectory()
    out_dir = temp_dir.name
    while True:
        batchfiles = db.select()
        if len(batchfiles) > 0:

            batchfile = batchfiles[0]
            source_file = batchfile.filename

            logging.debug(f"Processing: {source_file} - for {batchfile.email} - pending {len(batchfiles)}")

            model = _get_model_file(batchfile.model_name)
            source_file_base = os.path.basename(source_file)
            processed = ProcessedFiles(source_file_base)

            converted_audio = os.path.join(out_dir, WAV_FILE)
            timeout = _get_timeout()
            inference_time, result = execution.run_inference(source_file, batchfile.original_filename, model, converted_audio, timeout)

            if result == Command().TIMEOUT_ERROR:
                msg = f"Ha trigat massa temps en processar-se. Envieu un fitxer més curt. Aturem l'operació després de {timeout} segons de processament."
                _send_mail_error(batchfile, inference_time, source_file_base, msg)
                continue

            if result != Command().NO_ERROR:
                _send_mail_error(batchfile, inference_time, source_file_base, "Reviseu que sigui un d'àudio o vídeo vàlid.")
                continue

            target_file_srt = converted_audio + ".srt"
            target_file_txt = converted_audio + ".txt"
            extension = _get_extension(batchfile.original_filename)
            _send_mail(batchfile, inference_time, source_file_base)

            processed.move_file(batchfile.filename_dbrecord)
            processed.move_file(target_file_srt)
            processed.move_file(target_file_txt)
            processed.move_file_bin(source_file, extension)

        now = time.time()
        if now > purge_last_time + PURGE_INTERVAL_SECONDS:
            purge_last_time = now
            logging.debug(f"Purging {datetime.datetime.now()}")
            ProcessedFiles.purge_files(PURGE_OLDER_THAN_DAYS)

        time.sleep(30)

if __name__ == "__main__":
    main()
