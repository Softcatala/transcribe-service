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

from processedfiles import ProcessedFiles
import unittest
import os
import tempfile
import time

class TestProcessedFiles(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ENTRIES = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create(self):
        HOURS_DAY = 24
        MINUTES_HOUR = 60
        MINUTES_SEC = 60
        for day in range(0, 10):
            filename = os.path.join(self.temp_dir.name, f"file-{day}")
            with open(filename, "w") as file:
                file.write("Hello")

            old_time = time.time() - (HOURS_DAY * MINUTES_HOUR * MINUTES_SEC * day)
            os.utime(filename, (old_time, old_time))

        deleted = ProcessedFiles.purge_files(3, self.temp_dir.name)
        self.assertEquals(7, deleted)

if __name__ == '__main__':
    unittest.main()
