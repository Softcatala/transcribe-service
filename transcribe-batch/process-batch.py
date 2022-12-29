#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from processedfilesdb import ProcessedFilesDB
from sendmail import Sendmail
import datetime

def init_logging():

    logfile = 'process-batch.log'

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


MAX_SIZE = 8192 * 1024

def truncate_file(filename):
    f = open(filename, "a")
    f.truncate(MAX_SIZE)
    f.close()

def main():

    print("Process batch files to transcribe")
    init_logging()
    db = BatchFilesDB()
    ProcessedFilesDB.ensure_dir()

    while True:
        batchfiles = db.select()
        if len(batchfiles) > 0:

            batchfile = batchfiles[0]
            source_file = batchfile.filename
            logging.debug(f"Processing: {source_file} - for {batchfile.email} - pending {len(batchfiles)}")

            truncate_file(source_file)
            attachment = True
            outdir = "outdir/"

            print(f"batchfile.model_name: {batchfile.model_name}")
            if batchfile.model_name == "small":
                model = "small"
            elif batchfile.model_name == "medium":
                model = "medium"
            elif batchfile.model_name == "large":
                model = "large-v2"
            elif batchfile.model_name == "sc-small":
                model = "sc-small"
            else: # default
                model = "tiny"

            cmd = f"whisper --fp16 False --threads 16 --language ca --model {model} {source_file} -o {outdir} > /dev/null"

            start_time = datetime.datetime.now()
            os.system(cmd)
            end_time = datetime.datetime.now() - start_time

            source_file_base = os.path.basename(source_file)
            processed = ProcessedFilesDB(source_file_base)
            target_file_srt = os.path.join(outdir, source_file_base + ".srt")
            target_file_txt = os.path.join(outdir, source_file_base + ".txt")            

            logging.debug(f"Run {cmd} in {end_time}")
            
            text = f"Ja tenim el vostre fitxer '{batchfile.original_filename}' transcrit amb el model '{model}'. El podeu baixar des de "
            text += f"https://web2015.softcatala.org/transcripcio/bentornat/?uuid={source_file_base}"
            Sendmail().send(text, batchfile.email, target_file_srt)

          #  processed.copy_file(batchfile.filename_dbrecord)
            processed.move_file(target_file_srt)
            processed.move_file(target_file_txt)

            db.delete(batchfile.filename_dbrecord)
            os.remove(source_file)

        time.sleep(30)


if __name__ == "__main__":
    main()
