# -*- encoding: utf-8 -*-
#
# Copyright (c) 2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import os
import uuid
import fnmatch
import logging
from predicttime import PredictTime
from typing import Optional
from similarusers import SimilarUsers

class BatchFile():
    def __init__(self,
                 filename_dbrecord: str,
                 filename: str,
                 email: str,
                 model_name: str,
                 original_filename: str,
                 estimated_time: int,
                 highlight_words: Optional[int] = None,
                 num_chars: Optional[int] = None,
                 num_sentences: Optional[int] = None):
                 
        self.filename_dbrecord = filename_dbrecord
        self.filename = filename
        self.email = email
        self.model_name = model_name
        self.original_filename = original_filename
        self.estimated_time = estimated_time
        self.highlight_words = highlight_words
        self.num_chars = num_chars
        self.num_sentences = num_sentences

# This is a disk based priority queue with works as filenames
# as items to store
class Queue(): # works with filenames
    g_check_directory = True
    def __init__(self, entries = '/srv/data/entries'):
        self.ENTRIES = entries

    def _find(self, directory, pattern):
        filelist = []

        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    filelist.append(filename)

        filelist.sort(key=lambda filename: os.path.getmtime(filename))
        return filelist

    def count(self):
        filenames = self._find(self.ENTRIES, "*.dbrecord")
        return len(filenames)

    def get_all(self):
        return self._find(self.ENTRIES, "*.dbrecord")

    def put(self, filename_dbrecord, content):
        if self.g_check_directory:
            self.g_check_directory = False
        if not os.path.exists(self.ENTRIES):
            os.makedirs(self.ENTRIES)

        with open(filename_dbrecord, "w") as fh:
            fh.write(content)

    def delete(self, filename):
        os.remove(filename)



class BatchFilesDB(Queue):

    SEPARATOR = "\t"

    def get_record_file_from_uuid(self, _uuid):
        return os.path.join(self.ENTRIES, _uuid + ".dbrecord")

    def get_new_uuid(self):
        return str(uuid.uuid4())

    def _optional_int(self, string):
        return None if string == "None" or len(string) == 0 else int(string)

    def _optional_bool(self, string):
        return None if string == "None" or len(string) == 0 else string == "True"

    def _estimate_time(self, filename, original_filename):
        try:
            predictTime = PredictTime()
            predictTime.load()
            return predictTime.predict_time_from_filename(filename, original_filename)

        except Exception as exception:
            logging.error("_estimate_time. Error:" + str(exception))
            return PredictTime().CANNOT_PREDICT

    def create(self, filename, email, model_name, original_filename, highlight_words = None,
                  num_chars = None, num_sentences = None, record_uuid = None):

        if not record_uuid:
            record_uuid = self.get_new_uuid()

        filename_dbrecord = self.get_record_file_from_uuid(record_uuid)
        _estimated_time = self._estimate_time(filename, original_filename)
        line =  f"v2{self.SEPARATOR}{filename}{self.SEPARATOR}{email}{self.SEPARATOR}{model_name}{self.SEPARATOR}{original_filename}{self.SEPARATOR}{_estimated_time}"
        line += f"{self.SEPARATOR}{highlight_words}{self.SEPARATOR}{num_chars}{self.SEPARATOR}{num_sentences}"
        self.put(filename_dbrecord, line)
        return record_uuid

    def estimated_queue_waiting_time(self) -> str:
        filenames = self.get_all()
        waiting_time = 0
        for filename in filenames:
            record = self._read_record(filename)
            
            if record.estimated_time == PredictTime().CANNOT_PREDICT:
                return ""
            
            waiting_time += record.estimated_time

        clients = int(os.environ.get('CLIENTS', 1))
        waiting_time = int(waiting_time / clients)
        return PredictTime().get_formatted_time(waiting_time)

    def select(self, email = None):
        filenames = self.get_all()
        records = []
        for filename in filenames:
            record = self._read_record(filename)

            if email and record.email.lower() != email.lower():
                continue

            records.append(record)

        return records
        
    def get_count_of_files_for_similar_users(self, email):
        records = self.select()
        email_list = list(map(lambda record: record.email, records))
        similar_users = SimilarUsers()
        return similar_users.get_count_of_files_for_similar_users(email_list, email)

    def _read_record_from_uuid(self, _uuid):
        record_fullpath = os.path.join(self.ENTRIES, _uuid + ".dbrecord")
        record = self._read_record(record_fullpath)
        return record

    def _read_record(self, filename_dbrecord):
        try:
            with open(filename_dbrecord, "r") as fh:
                line = fh.readline()
                components = line.split(self.SEPARATOR)
                if components[0] == "v2":
                     return BatchFile(filename_dbrecord = filename_dbrecord,
                                     filename = components[1],
                                     email = components[2],
                                     model_name = components[3],
                                     original_filename = components[4],
                                     estimated_time = int(components[5]),
                                     highlight_words = self._optional_bool(components[6]),
                                     num_chars = self._optional_int(components[7]),
                                     num_sentences = self._optional_int(components[8]))
                else:
                    raise RuntimeError("dbrecord version not supported")

        except Exception as exception:
            logging.error(f"_read_record. Unable to read {filename_dbrecord}. Error: {exception}")
            return None
