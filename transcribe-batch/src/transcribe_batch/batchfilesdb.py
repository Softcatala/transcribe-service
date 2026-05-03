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
from typing import Optional


class BatchFile:
    def __init__(
        self,
        filename_dbrecord: str,
        filename: str,
        email: str,
        model_name: str,
        original_filename: str,
        delete_token: str,
        highlight_words: Optional[bool] = None,
        num_chars: Optional[int] = None,
        num_sentences: Optional[int] = None,
    ):
        self.filename_dbrecord = filename_dbrecord
        self.filename = filename
        self.email = email
        self.model_name = model_name
        self.original_filename = original_filename
        self.delete_token = delete_token
        self.highlight_words = highlight_words
        self.num_chars = self._safe_int(num_chars)
        self.num_sentences = self._safe_int(num_sentences)

    @staticmethod
    def _safe_int(value) -> Optional[int]:
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


# This is a disk based priority queue with works as filenames
# as items to store
class Queue:  # works with filenames
    g_check_directory = True

    def __init__(self, entries="/srv/data/entries"):
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
        try:
            return None if string == "None" or len(string) == 0 else int(string)
        except Exception as e:
            logging.error(f"_optional_int. Error: {e}")
            return None

    def _optional_bool(self, string):
        try:
            return None if string == "None" or len(string) == 0 else string == "True"
        except Exception as e:
            logging.error(f"_optional_bool. Error: {e}")
            return None

    def create(
        self,
        filename,
        email,
        model_name,
        original_filename,
        highlight_words=None,
        num_chars=None,
        num_sentences=None,
        record_uuid=None,
    ):
        if not record_uuid:
            record_uuid = self.get_new_uuid()

        filename_dbrecord = self.get_record_file_from_uuid(record_uuid)
        dt_token = self.get_new_uuid()
        delete_token = f"dt_{dt_token}"
        line = f"v2{self.SEPARATOR}{filename}{self.SEPARATOR}{email}{self.SEPARATOR}{model_name}{self.SEPARATOR}{original_filename}{self.SEPARATOR}{delete_token}"
        line += f"{self.SEPARATOR}{highlight_words}{self.SEPARATOR}{num_chars}{self.SEPARATOR}{num_sentences}"
        self.put(filename_dbrecord, line)
        return record_uuid

    def select(self, email=None):
        filenames = self.get_all()
        records = []
        for filename in filenames:
            record = self._read_record(filename)

            if email and record.email.lower() != email.lower():
                continue

            records.append(record)

        return records

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
                    return BatchFile(
                        filename_dbrecord=filename_dbrecord,
                        filename=components[1],
                        email=components[2],
                        model_name=components[3],
                        original_filename=components[4],
                        delete_token=components[5],
                        highlight_words=self._optional_bool(components[6]),
                        num_chars=self._optional_int(components[7]),
                        num_sentences=self._optional_int(components[8]),
                    )
                else:
                    raise RuntimeError("dbrecord version not supported")

        except Exception as exception:
            logging.error(
                f"_read_record. Unable to read {filename_dbrecord}. Error: {exception}"
            )
            return None
