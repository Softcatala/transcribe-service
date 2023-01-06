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

PROCESSED = '/srv/data/processed'

class ProcessedFilesDB():

    def __init__(self, uuid):
        self.uuid = uuid

    def is_valid_uuid(self):
        try:
            uuid.UUID(str(self.uuid))
            return True
        except ValueError:
            return False

    def ensure_dir():
        if not os.path.exists(PROCESSED):
            os.makedirs(PROCESSED)

    def copy_file(self, full_filename):
        filename = os.path.basename(full_filename)
        target = os.path.join(PROCESSED, filename)
        shutil.copy(full_filename, target)
        logging.debug(f"Copy file {full_filename} to {target}")

    def move_file(self, full_filename):
        filename = os.path.basename(full_filename)
        target = os.path.join(PROCESSED, filename)
        shutil.move(full_filename, target)
        logging.debug(f"Moved file {full_filename} to {target}")

    def move_file_bin(self, full_filename, extension):
        filename = os.path.basename(full_filename)
        target = os.path.join(PROCESSED, f"{filename}{extension}")
        shutil.move(full_filename, target)

        logging.debug(f"Moved file {full_filename} to {target}")

    def get_binary(self, allowed_extensions):
        fullname = os.path.join(PROCESSED, self.uuid)
        filename = ""
        ext = ""
        for _ext in allowed_extensions:
            filename = f"{fullname}.{_ext}"
            if os.path.exists(filename):
                ext = _ext
                break

        logging.debug(f"_get_binary {uuid} -> {filename}")
        return filename, ext
