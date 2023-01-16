# -*- encoding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import logging
import shutil
import uuid
import time
import fnmatch

PROCESSED = '/srv/data/processed'

class ProcessedFiles():

    def __init__(self, uuid):
        self.uuid = uuid
        
    def get_processed_directory():
        return PROCESSED

    def is_valid_uuid(self):
        try:
            uuid.UUID(str(self.uuid))
            return True
        except ValueError:
            return False

    def do_files_exists(self):
        extensions = ["txt", "srt"]
        for extension in extensions:
            fullname = os.path.join(PROCESSED, self.uuid)
            fullname = f"{fullname}.{extension}"

            if not os.path.exists(fullname):
                message = f"file {extension} does not exist"
                return False, message

        return True, ""

    def ensure_dir():
        if not os.path.exists(PROCESSED):
            os.makedirs(PROCESSED)

    def _get_extension(self, filename):
        split_tup = os.path.splitext(filename)
        file_extension = split_tup[1]
        return file_extension

    def copy_file(self, full_filename):
        filename = os.path.basename(full_filename)
        target = os.path.join(PROCESSED, filename)
        shutil.copy(full_filename, target)
        logging.debug(f"Copy file {full_filename} to {target}")

    def move_file(self, full_filename):
        filename = os.path.basename(full_filename)
        ext = self._get_extension(filename)
        target = os.path.join(PROCESSED, f"{self.uuid}{ext}")
        shutil.move(full_filename, target)
        logging.debug(f"Moved file {full_filename} to {target}")

    def move_file_bin(self, full_filename, extension):
        filename = os.path.basename(full_filename)
        target = os.path.join(PROCESSED, f"{self.uuid}{extension}")
        shutil.move(full_filename, target)

        logging.debug(f"Moved file {full_filename} to {target}")

    def _find_files(directory, pattern):
        filelist = []

        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    filelist.append(filename)

        return filelist

    def purge_files(days, directory = PROCESSED):
        HOURS_DAY = 24
        MINUTES_HOUR = 60
        MINUTES_SEC = 60
        deleted = 0

        files = ProcessedFiles._find_files(directory, "*")
        time_limit = time.time() - (HOURS_DAY * MINUTES_HOUR * MINUTES_SEC * days)
        for file in files:
            file_time = os.stat(file).st_mtime
            if file_time < time_limit:
                try:
                    os.remove(file)
                    logging.debug(f"Deleted file: {file}")
                    deleted += 1
                except Exception as e:
                    logging.error(f"Error deleting file {file}: {e}")

        return deleted
