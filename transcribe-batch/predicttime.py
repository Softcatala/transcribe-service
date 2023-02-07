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

import logging
import os
import datetime

class PersitedList():

    def __init__(self, filename):
        self.FILENAME = filename
        self.data = []

    def get(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)

    def load(self):
        self.data = []
        if os.path.exists(self.FILENAME):
            with open(self.FILENAME, 'r') as f:
                for line in f.readlines():
                    self.data.append(line.rstrip())

    def save(self):
        with open(self.FILENAME, 'w') as f:
            for s in self.data:
                f.write(str(s) + '\n')


'''
    The goal is to persist a list of max samples of inference time per format (e.g mp3)
        mp3 - 10K - 10s date
        mp3 - 20K - 20s date
        mp4 - 24K - 10s date

    To be able then to predict how long the inference will take for a file that we have not seen
'''
class PredictTime(PersitedList):

    SEPARATOR = "\t"
    CANNOT_PREDICT = -1

    def __init__(self, filename = "/srv/data/stats.txt"):
        PersitedList.__init__(self, filename)
        self.MAX_SAMPLES_PER_FORMAT = 10
        self.format_time = {} # mb/s

    def _remove_samples_if_necessary(self, _format: str):
        first_idx = -1
        count = 0
        for idx in range(0, len(self.data)):
            line = self.data[idx]
            components = line.split(self.SEPARATOR)
            _format_local = components[0]
            if _format_local == _format:
                count += 1
                if first_idx == -1:
                    first_idx = idx

        if count == self.MAX_SAMPLES_PER_FORMAT:
            del self.data[first_idx]
            logging.debug("_remove_samples_if_necessary.removed: " + self.data[first_idx])

    def append(self, _format: str, length: int, time: int):
        self._remove_samples_if_necessary(_format)
        now = datetime.datetime.now()
        line = f"{_format}{self.SEPARATOR}{length}{self.SEPARATOR}{time}{self.SEPARATOR}{now}"
        logging.debug(f"PredictTime.append: {line}")
        self.data.append(line)
        self.format_time = {}

    def _compute_time_size(self):
        if len(self.format_time) > 0:
            return

        format_length = {}
        format_time_local = {}
        for line in self.data:
            components = line.split(self.SEPARATOR)
            _format = components[0]
            length = int(components[1])
            time = int(components[2])

            total_length = format_length.get(_format)
            if not total_length:
                total_length = 0

            total_length += length

            total_time = format_time_local.get(_format)
            if not total_time:
                total_time = 0

            total_time += time
            format_length[_format] = total_length
            format_time_local[_format] = total_time

        for _format in format_time_local:
            _time = format_time_local[_format]
            length_mb = format_length[_format] / 1024 / 1024
            ratio = length_mb / _time
            self.format_time[_format] = ratio

    def load(self):
        super().load()
        self.format_time = {}
        
    def get_formatted_time(self, seconds : int):
        try:

            delta = datetime.timedelta(seconds=seconds)
            _time = str(delta)
            HOUR_MIN_SECONDS = 3
            components = _time.split(':')
            if len(components) != HOUR_MIN_SECONDS:
                return _time

            hours = components[0]
            minutes = components[1]
            seconds = components[2]

            if int(hours) == 0:
                if int(minutes) == 0:
                    return f"{seconds}s".lstrip("0")
                else:
                    return f"{minutes}m".lstrip("0")

            return f"{hours}h {minutes}m".lstrip("0")

        except Exception as exception:
            logging.error(f"get_formatted_time. Error: {exception}")
            return _time
        

    def predict_time_from_filename(self, filename: str, original_filename: str) -> int:
        try:
            _format = original_filename.rsplit('.', 1)[1].lower()

            if not os.path.exists(filename):
                return self.CANNOT_PREDICT

            length = os.path.getsize(filename)
            prediction = self.predict_time(_format, length)
            return prediction

        except Exception as exception:
            logging.error("PredictTime. predict_time_from_filename. Error:" + str(exception))
            return self.CANNOT_PREDICT

    def predict_time(self, _format: str, length: int) -> int:
        self._compute_time_size()
        ratio = self.format_time.get(_format)
        if not ratio:
            logging.debug(f"predict_time: no data for {_format} format")
            return self.CANNOT_PREDICT

        prediction = int(length / 1024 / 1024 / ratio)
        return prediction
