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
from lockfile import LockFile
import datetime
import tempfile
from usage import Usage


def init_logging():
    LOGDIR = os.environ.get("LOGDIR", "")
    LOGID = os.environ.get("LOGID", "0")
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
    logfile = os.path.join(LOGDIR, f"process-batch-{LOGID}.log")
    logger = logging.getLogger()
    hdlr = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=1024 * 1024, backupCount=1
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
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
        model = "small"
    elif model_name == "medium":
        model = "medium"
    else:  # default
        model = "medium"

    return model


def _get_threads():
    return os.environ.get("THREADS", 4)


def _get_timeout() -> int:
    return int(os.environ.get("TIMEOUT_CMD", 60 * 90))


def _send_mail(batchfile, inference_time, source_file_base):
    context = {
        "uuid": source_file_base,
        "filename": batchfile.original_filename,
        "model": batchfile.model_name,
    }
    Sendmail().send_html(batchfile.email, "transcription-finished", context)


def _send_mail_error(batchfile, inference_time, source_file_base, message):
    logging.info(f"_send_mail_error: {message} to {batchfile.email}")
    context = {
        "message": message,
        "filename": batchfile.original_filename,
        "model": batchfile.model_name,
    }
    Sendmail().send_html(batchfile.email, "transcription-error", context)


def _delete_record(db, batchfile, converted_audio):
    db.delete(batchfile.filename_dbrecord)

    if os.path.isfile(batchfile.filename):
        os.remove(batchfile.filename)
        logging.debug(f"Deleted {batchfile.filename}")

    if os.path.exists(converted_audio):
        os.remove(converted_audio)

    LockFile(batchfile.filename_dbrecord).delete()


def main():
    print("Process batch files to transcribe")
    init_logging()
    db = BatchFilesDB()
    ProcessedFiles.ensure_dir()
    purge_last_time = time.time()
    PURGE_INTERVAL_SECONDS = 60 * 60 * 6  # For times per day
    PURGE_OLDER_THAN_DAYS = 3
    WAV_FILE = "file.wav"
    execution = Execution(_get_threads())

    temp_dir = tempfile.TemporaryDirectory()
    out_dir = temp_dir.name
    while True:
        batchfiles = db.select()
        for idx in range(len(batchfiles) - 1, -1, -1):
            batchfile = batchfiles[idx]
            if LockFile(batchfile.filename_dbrecord).has_lock():
                batchfiles.remove(batchfile)

        if len(batchfiles) > 0:
            batchfile = batchfiles[0]
            if not LockFile(batchfile.filename_dbrecord).create():
                time.sleep(5)
                continue

            source_file = batchfile.filename

            logging.info(
                f"Processing: {source_file} - for {batchfile.email} - pending {len(batchfiles)}"
            )

            model = _get_model_file(batchfile.model_name)
            source_file_base = os.path.basename(source_file)
            processed = ProcessedFiles(source_file_base)

            converted_audio = os.path.join(out_dir, WAV_FILE)

            timeout = _get_timeout()
            result = execution.run_conversion(
                batchfile.original_filename, source_file, converted_audio, timeout
            )

            if result != Command.NO_ERROR:
                _delete_record(db, batchfile, converted_audio)
                msg = "No s'ha pogut llegir el fitxer. Normalment, això succeeix perquè el fitxer que heu enviat no és d'àudio o vídeo o és malmès.\n"
                msg += "Si està malmès, podeu provar de convertir-lo a un altre format (procés que sol reparar el fitxer) a https://online-audio-converter.com/\n"
                msg += "i tornar-nos a enviar la versió convertida."
                Usage().log("conversion_error")
                _send_mail_error(batchfile, 0, source_file_base, msg)
                continue

            (
                inference_time,
                result,
                target_file_txt,
                target_file_srt,
                target_file_json,
            ) = execution.run_inference(
                source_file,
                batchfile.original_filename,
                model,
                converted_audio,
                timeout,
                batchfile.highlight_words,
                batchfile.num_chars,
                batchfile.num_sentences,
            )

            if result == Command.TIMEOUT_ERROR:
                _delete_record(db, batchfile, converted_audio)
                minutes = int(timeout / 60)
                msg = f"Ha trigat massa temps en processar-se. Aturem l'operació després de {minutes} minuts de processament.\n"
                msg += "Podeu enviar fitxers més curts, usar un model petit o bé usar el client Buzz per fer-ho al vostre PC."
                Usage().log("whisper_timeout")
                _send_mail_error(batchfile, inference_time, source_file_base, msg)
                continue

            if result != Command.NO_ERROR:
                _delete_record(db, batchfile, converted_audio)
                _send_mail_error(
                    batchfile,
                    inference_time,
                    source_file_base,
                    "Reviseu que sigui un d'àudio o vídeo vàlid.",
                )
                Usage().log("whisper_returns_error")
                continue

            language = execution.get_transcription_language(target_file_txt)
            if language in ["es", "en", "fr"]:
                _delete_record(db, batchfile, converted_audio)
                msg = "Aquest servei només transcriu textos en català. El fitxer que heu enviat és en un altra llengua.\n"
                _send_mail_error(batchfile, inference_time, source_file_base, msg)
                logging.info(
                    f"Non-Catalan language detected: '{language}' for '{batchfile.original_filename}'"
                )
                Usage().log("whisper_not_catalan")
                continue

            extension = _get_extension(batchfile.original_filename)
            _send_mail(batchfile, inference_time, source_file_base)
            logging.info(f"File for {batchfile.email} completed in {inference_time}")

            processed.move_file(batchfile.filename_dbrecord)
            processed.move_file(target_file_srt)
            processed.move_file(target_file_txt)
            processed.move_file(target_file_json)
            processed.move_file_bin(source_file, extension)
            LockFile(batchfile.filename_dbrecord).delete()

        now = time.time()
        if now > purge_last_time + PURGE_INTERVAL_SECONDS:
            purge_last_time = now
            purged = ProcessedFiles.purge_files(PURGE_OLDER_THAN_DAYS)
            logging.info(f"Purging {datetime.datetime.now()}, {purged} files deleted")

        time.sleep(30)


if __name__ == "__main__":
    main()
