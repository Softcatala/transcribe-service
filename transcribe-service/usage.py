#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import datetime
from shutil import copyfile
import logging
import multiprocessing

lock = multiprocessing.Lock()

"""
    This class keeps a log of the usage of a service
        - For usage write a line on the file with the date
        - At the number of days specified cleans old entries
"""


class Usage(object):
    FILE = "/srv/data/usage.txt"
    DAYS_TO_KEEP = 7
    rotate = True

    def _set_filename(self, filename):
        self.FILE = filename

    def _get_time_now(self):
        return datetime.datetime.utcnow()

    def get_date_from_line(self, line):
        return line.split("\t", 1)[0]

    def log(self, action):
        current_time = self._get_time_now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with lock:
                with open(self.FILE, "a+") as file_out:
                    file_out.write(f"{current_time}\t{action}\n")

                if self.rotate and self._is_old_line(self._read_first_line()):
                    self._rotate_file()
        except Exception as exception:
            logging.error("Usage.log. Error:" + str(exception))
            pass

    def _get_line_components(self, line):
        components = line.strip().split("\t")
        return components[0], components[1]

    def get_stats(self, date_requested):
        results = {}
        try:
            with open(self.FILE, "r") as file_in:
                for line in file_in:
                    date_component, action = self._get_line_components(line)

                    datetime_no_newline = date_component
                    line_datetime = datetime.datetime.strptime(
                        datetime_no_newline, "%Y-%m-%d %H:%M:%S"
                    )
                    if line_datetime.date() != date_requested.date():
                        continue

                    cnt = results.get(action)
                    if cnt:
                        cnt += 1
                    else:
                        cnt = 1

                    results[action] = cnt

        except Exception as exception:
            logging.error("Usage.get_stats. Error:" + str(exception))
            pass

        return results

    def _read_first_line(self):
        try:
            with open(self.FILE, "r") as f:
                first = f.readline()
                return first
        except IOError:
            return None

    def _is_old_line(self, line):
        if line is None:
            return False

        invalid = False

        try:
            line = self.get_date_from_line(line)
            line_datetime = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S")

        except Exception as exception:
            logging.error("Usage._is_old_line. Error:" + str(exception))
            invalid = True

        now = self._get_time_now() - datetime.timedelta(days=self.DAYS_TO_KEEP)
        return invalid or line_datetime.date() <= now.date()

    def _rotate_file(self):
        NEW = "usage.new"
        directory = os.path.dirname(os.path.abspath(self.FILE))
        new_file = os.path.join(directory, NEW)

        with open(self.FILE, "r") as temp:
            with open(new_file, "w") as new:
                for line in temp:
                    if self._is_old_line(line) is False:
                        new.write(line)

        copyfile(new_file, self.FILE)
        os.remove(new_file)
