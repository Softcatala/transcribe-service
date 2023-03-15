#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import time

class LockFile():

    def __init__(self, filename):
        self.filename = filename + ".lock"

    def create(self):
        try:
            fh = open(self.filename, "x")
            fh.write("")
            fh.close()
        except Exception as e:
            logging.debug(f"LockFile.create. Failed to create lock for {self.filename} - {str(e)}")
            return False

        logging.debug(f"LockFile.create. Created {self.filename}")
        return True

    def delete(self):
        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
                logging.debug(f"LockFile.delete. Removing lock: {self.filename}")
            except Exception as e:
                logging.error(f"LockFile.delete. Error deleting file {self.filename}: {e}")

    def has_lock(self):
        has_lock = False
        if not os.path.exists(self.filename):
            return has_lock

        MINUTES_HOUR = 60
        MINUTES_SEC = 60
        time_limit = time.time() - (MINUTES_HOUR * MINUTES_SEC * 3)
        file_time = os.stat(self.filename).st_mtime
        if file_time < time_limit:
            logging.debug(f"LockFile.has_lock. Lock has expired: {self.filename}")
            self.delete()
        else:
            has_lock = True

        return has_lock

