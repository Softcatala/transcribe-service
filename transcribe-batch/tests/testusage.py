# -*- coding: utf-8 -*-
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

import unittest
import os
import datetime
from usage import Usage


class UsageTest(Usage):
    datetime = None

    def __init__(self):
        self._set_filename("usage.txt")

    def _get_time_now(self):
        return self.datetime

    def _set_time_now(self, value):
        self.datetime = value


class TestUsage(unittest.TestCase):
    def setUp(self):
        filename = UsageTest().FILE
        if os.path.exists(filename):
            os.remove(filename)

    def readLog(self):
        with open(UsageTest().FILE, "r") as temp:
            return temp.readlines()

    def _test_log_one(self):
        usage = UsageTest()
        usage.rotate = False
        usage._set_time_now(datetime.datetime(2016, 10, 5))
        usage.log("conversion_error")
        lines = self.readLog()

        self.assertEqual(len(lines), 1)
        self.assertEqual("2016-10-05 00:00:00	conversion_error\n", lines[0])

    def test_log_rotate(self):
        usage = UsageTest()
        usage._set_time_now(datetime.datetime(2017, 10, 8, 13, 00, 00))
        usage.log("conversion_error")

        usage._set_time_now(datetime.datetime(2017, 10, 8, 15, 00, 00))
        usage.log("conversion_error")

        usage._set_time_now(
            datetime.datetime(2017, 10, 8 + usage.DAYS_TO_KEEP, 14, 00, 00)
        )
        usage.log("conversion_error")

        lines = self.readLog()
        self.assertEqual(len(lines), 1)

    def _test_is_old_line_true(self):
        usage = UsageTest()
        usage._set_time_now(datetime.datetime(2016, 11, 5))
        is_old = usage._is_old_line("2016-10-05 00:00:00	conversion_error\n")
        self.assertEqual(True, is_old)

    def _test_is_old_line_false(self):
        usage = UsageTest()
        usage._set_time_now(datetime.datetime(2016, 11, 5))
        is_old = usage._is_old_line("2016-11-05 00:00:00	conversion_error\n")
        self.assertEqual(False, is_old)

    def _test_is_old_line_exception(self):
        usage = UsageTest()
        usage._set_time_now(datetime.datetime(2016, 11, 5))
        is_old = usage._is_old_line("INVALID DATE conversion_error\n")
        self.assertEqual(True, is_old)


if __name__ == "__main__":
    unittest.main()
