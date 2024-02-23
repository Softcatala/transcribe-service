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
import subprocess
import threading
import tempfile
from predicttime import PredictTime
import signal
import psutil
from typing import Optional

class Command(object):

    TIMEOUT_ERROR = -1
    NO_ERROR = 0

    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    # Make sure that you kill also the process started in the Shell
    def _kill_child_processes(self, parent_pid, sig=signal.SIGTERM):
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            logging.error(f"_kill_child_processes.Cannot kill process {parent_pid}")
            return

        children = parent.children(recursive=True)
        for process in children:
            process.send_signal(sig)

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self._kill_child_processes(self.process.pid)
            return self.TIMEOUT_ERROR

        return self.process.returncode


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

    def _log_predicted_vs_real(self, predicted, real):
        if predicted == PredictTime().CANNOT_PREDICT or predicted == 0:
            return

        diff = (real / predicted * 100) - 100
        logging.debug(f" _log_predicted_vs_real. Predicted: {predicted}, real: {real}, diff {diff:.0f}%")

    def _ffmpeg_errors(self, ffmpeg_errfile):
        return_code = Command.NO_ERROR
        try:
            if os.path.getsize(ffmpeg_errfile) == 0:
                return return_code

            return_code = -1
            cnt = 0
            with open(ffmpeg_errfile, "r") as fh:
                for line in fh.readlines():
                    logging.debug(f"_ffmpeg_errors: {line.rstrip()}")
                    if cnt > 5:
                        break

                    cnt += 1

            return return_code
        except Exception as exception:
            logging.error(f"_ffmpeg_errors. Error: {exception}")
            return return_code

    def _run_ffmpeg(self, source_file, converted_audio, timeout):
        ffmpeg_errfile = "ffmpeg-error.log"
        cmd = f"ffmpeg -i {source_file} -ar 16000 -ac 1 -c:a pcm_s16le {converted_audio} -y -loglevel error 2>{ffmpeg_errfile} > /dev/null"
        Command(cmd).run(timeout=timeout)
        result = self._ffmpeg_errors(ffmpeg_errfile)
        logging.debug(f"Run {cmd} with result {result}")
        return result

    def _get_extension(self, filename):
        extension = "mp4"
        split_tup = os.path.splitext(filename)
        if len(split_tup) > 0 and len(split_tup[1]) > 0:
            extension = split_tup[1]
            extension = extension[1:]

        return extension

    def _sox_errors(self, sox_errfile):
        return_code = Command.NO_ERROR
        try:
            if os.path.getsize(sox_errfile) == 0:
                return return_code

            return_code = -1
            cnt = 0
            with open(sox_errfile, "r") as fh:
                for line in fh.readlines():
                    if cnt > 5:
                        break

                    logging.debug(f"_sox_errors: {line.rstrip()}")
                    cnt += 1

            return return_code
        except Exception as exception:
            logging.error(f"_sox_errors. Error: {exception}")
            return return_code

    def run_conversion(self,
                       original_filename: str,
                       source_file: str,
                       converted_audio: str,
                       timeout: int):

        result = self._run_ffmpeg(source_file, converted_audio, timeout)
        if result != Command.NO_ERROR:
            converted_audio_fix = tempfile.NamedTemporaryFile().name + ".wav"

            _format = self._get_extension(original_filename)
            sox_errfile = "sox-error.log"

            cmd = f"sox -t {_format} {source_file} {converted_audio_fix} 2> {sox_errfile}"
            Command(cmd).run(timeout=timeout)
            result = self._sox_errors(sox_errfile)
            logging.debug(f"Run {cmd} with result {result}")
            if result != Command.NO_ERROR:
                return result

            result = self._run_ffmpeg(converted_audio_fix, converted_audio, timeout)

        return result


    def _whisper_errors(self, whisper_errfile):
        try:
            if os.path.getsize(whisper_errfile) == 0:
                return

            with open(whisper_errfile, "r") as fh:
                for line in fh.readlines():
                    logging.debug(f"_whisper_errors: {line.rstrip()}")

        except Exception as exception:
            logging.error(f"whisper_errfile. Error: {exception}")


    def run_inference(self,
                    source_file: str,
                    original_filename: str,
                    model: str,
                    converted_audio: str,
                    timeout: int,
                    highlight_words: Optional[int] = None,
                    num_chars: Optional[int] = None,
                    num_sentences: Optional[int] = None):

        WHISPER_PATH = "whisper-ctranslate2"
        OUTPUT_DIR = "output_dir/"
        options = ""
        word_timestamps = False

        if highlight_words:
            options += " --highlight_words True"
            word_timestamps = True
 
        if num_chars:
            options += f" --max_line_width {num_chars}"
            word_timestamps = True

        if num_sentences:
            options += f" --max_line_count {num_sentences}"
            word_timestamps = True

        if word_timestamps:
            options += f" --word_timestamps True"

        logging.debug(f"Options: {options}")
        start_time = datetime.datetime.now()
        predicted_time = self.predictTime.predict_time_from_filename(source_file, original_filename)
        if predicted_time != PredictTime().CANNOT_PREDICT:
            printable_time = PredictTime().get_formatted_time(predicted_time)
            logging.debug(f"Predicted time for {source_file} ({original_filename}): {printable_time}")

        compute_type = os.environ.get('COMPUTE_TYPE', "int8")
        verbose = os.environ.get('WHISPER_VERBOSE', "false").lower()
        device = os.environ.get("DEVICE", "cpu")
        device_index = os.environ.get("DEVICE_INDEX", "0")
        redirect = " > /dev/null" if verbose == "false" else ""

        whisper_errfile = "whisper_error.log"
        cmd = f"{WHISPER_PATH} {options} --pretty_json True --local_files_only True --compute_type {compute_type} --verbose True --threads {self.threads} --model {model} --output_dir {OUTPUT_DIR} --language ca --device {device} --device_index {device_index} {converted_audio} {redirect} 2> {whisper_errfile}"
        result = Command(cmd).run(timeout=timeout)
        self._whisper_errors(whisper_errfile)

        end_time = datetime.datetime.now() - start_time

        logging.debug(f"Run {cmd} in {end_time} with result {result}")
        if result == 0:
            self._persist_execution_stats(source_file, original_filename, end_time.seconds)
            
        if os.path.exists(converted_audio):
            os.remove(converted_audio)

        self._log_predicted_vs_real(predicted_time, end_time.seconds)
        filename = os.path.basename(converted_audio).rsplit(".", 1)[0]
        target_file_txt = os.path.abspath(os.path.join(OUTPUT_DIR, filename + ".txt"))
        target_file_srt = os.path.abspath(os.path.join(OUTPUT_DIR, filename + ".srt"))
        target_file_json = os.path.abspath(os.path.join(OUTPUT_DIR, filename + ".json"))
        return end_time, result, target_file_txt, target_file_srt, target_file_json
