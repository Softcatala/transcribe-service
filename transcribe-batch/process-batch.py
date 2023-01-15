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

def _run_inference(source_file, model, converted_audio):
    WHISPER_PATH = "/srv/whisper.cpp/"
    THREADS = _get_threads()

    start_time = datetime.datetime.now()

    cmd = f"ffmpeg -i {source_file} -ar 16000 -ac 1 -c:a pcm_s16le {converted_audio} -y 2> /dev/null > /dev/null"
    os.system(cmd)

    model_path = os.path.join(WHISPER_PATH, "sc-models", model)
    whisper_cmd = os.path.join(WHISPER_PATH, "main")
    cmd = f"{whisper_cmd} --threads {THREADS} -m {model_path} -f {converted_audio} -l ca -otxt -osrt 2> /dev/null > /dev/null"
    os.system(cmd)

    end_time = datetime.datetime.now() - start_time

    logging.debug(f"Run {cmd} in {end_time}")
    return end_time

def _send_mail(batchfile, inference_time, source_file_base):
    text = f"Ja tenim el vostre fitxer '{batchfile.original_filename}' transcrit amb el model '{batchfile.model_name}'. El podeu baixar des de "
    text += f"https://web2015.softcatala.org/transcripcio/resultats/?uuid={source_file_base}"

    if "@softcatala.org" in batchfile.email:
        THREADS = _get_threads()
        text += f"\nL'execució ha trigat {inference_time} amb {THREADS} threads."

    Sendmail().send(text, batchfile.email)

def main():

    print("Process batch files to transcribe")
    init_logging()
    db = BatchFilesDB()
    ProcessedFiles.ensure_dir()
    purge_last_time = time.time()
    PURGE_INTERVAL_SECONDS = 60 * 60 * 24 # Every day
    PURGE_OLDER_THAN_DAYS = 3
    WAV_FILE = "file.wav"

    temp_dir = tempfile.TemporaryDirectory()
    out_dir = temp_dir.name
    while True:
        batchfiles = db.select()
        if len(batchfiles) > 0:

            batchfile = batchfiles[0]
            source_file = batchfile.filename

            logging.debug(f"Processing: {source_file} - for {batchfile.email} - pending {len(batchfiles)}")

            print(f"batchfile.model_name: {batchfile.model_name}")
            model = _get_model_file(batchfile.model_name)

            db.delete(batchfile.filename_dbrecord) # In case it fails, we will not retry

            converted_audio = os.path.join(out_dir, WAV_FILE)
            inference_time = _run_inference(source_file, model, converted_audio)

            source_file_base = os.path.basename(source_file)
            processed = ProcessedFiles(source_file_base)

            target_file_srt = converted_audio + ".srt"
            target_file_txt = converted_audio + ".txt"
            extension = _get_extension(batchfile.original_filename)
            _send_mail(batchfile, inference_time, source_file_base)

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
