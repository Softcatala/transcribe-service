#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import datetime
import logging
import os
from predicttime import PredictTime
from command import Command

class Execution(object):


    def __init__(self, threads):
        self.threads = threads
        self.predictTime = PredictTime()
        self.predictTime.load()
        
    def _persist_execution_stats(self, source_file, original_filename, time):
        try:
            _format = original_filename.rsplit('.', 1)[1].lower()
            length = os.path.getsize(source_file)
            self.predictTime.append(_format, length, time)
            self.predictTime.save()

        except Exception as exception:
            logging.error("_persist_execution_stats. Error:" + str(exception))

    def run_inference(self, source_file, original_filename, model, converted_audio, timeout):
        WHISPER_PATH = "/srv/whisper.cpp/"

        start_time = datetime.datetime.now()
        predicted_time = self.predictTime.predict_time_from_filename(source_file, original_filename)
        if predicted_time:
            printable_time = PredictTime().get_formatted_time(predicted_time)
            logging.debug(f"Predicted time for {source_file} ({original_filename}): {printable_time}")

        cmd = f"ffmpeg -i {source_file} -ar 16000 -ac 1 -c:a pcm_s16le {converted_audio} -y 2> /dev/null > /dev/null"
        Command(cmd).run(timeout=timeout)

        model_path = os.path.join(WHISPER_PATH, "sc-models", model)
        whisper_cmd = os.path.join(WHISPER_PATH, "main")
        cmd = f"{whisper_cmd} --threads {self.threads} -m {model_path} -f {converted_audio} -l ca -otxt -osrt 2> /dev/null > /dev/null"
        result = Command(cmd).run(timeout=timeout)

        end_time = datetime.datetime.now() - start_time

        logging.debug(f"Run {cmd} in {end_time} with result {result}")
        if result == 0:
            self._persist_execution_stats(source_file, original_filename, end_time.seconds)

        if os.path.exists(converted_audio):
            os.remove(converted_audio)

        return end_time, result
