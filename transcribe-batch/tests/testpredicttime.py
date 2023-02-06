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

from predicttime import PredictTime
import unittest
import os
import tempfile
import sys

class TestPredictTime(unittest.TestCase):
    MB_BYTES = 1024*1024

    def _get_list(self):
        predictTime = PredictTime(tempfile.NamedTemporaryFile().name)
        return predictTime

    def test_append(self):
        predictTime = self._get_list()
        predictTime.append("mp3", "1000", "2000")
        self.assertEquals(1, len(predictTime))
        EXPECTED = "mp3\t1000\t2000"
        self.assertEquals(EXPECTED, predictTime.get(0)[0:len(EXPECTED)])

    def test_append_max_sample(self):
        predictTime = self._get_list()
        predictTime.append("mp3", "1", "1")
        predictTime.append("mp3", "2", "2")
        predictTime.append("mp3", "3", "3")
        predictTime.append("mp3", "4", "4")
        predictTime.append("mp3", "5", "5")
        predictTime.append("mp3", "6", "6")
        predictTime.append("mp3", "7", "7")
        self.assertEquals(5, len(predictTime))
        EXPECTED = "mp3\t3\t3"
        self.assertEquals(EXPECTED, predictTime.get(0)[0:len(EXPECTED)])
        EXPECTED = "mp3\t7\t7"
        self.assertEquals(EXPECTED, predictTime.get(4)[0:len(EXPECTED)])
        
    def test_save_load(self):
        predictTime = self._get_list()
        predictTime.append("mp4", "3000", "4000")
        predictTime.save()
        predictTime.load()
        EXPECTED = "mp4\t3000\t4000"
        self.assertEquals(EXPECTED, predictTime.get(0)[0:len(EXPECTED)])

    def test_predict_time(self):
        predictTime = self._get_list()
        predictTime.append("mp3", str(self.MB_BYTES * 10), str(5))
        predictTime.append("mp3", str(self.MB_BYTES * 20), str(10))
        
        seconds = predictTime.predict_time("mp3", self.MB_BYTES * 2)
        self.assertEquals(1, seconds)

    def test_predict_time_format_no_available(self):
        predictTime = self._get_list()
        seconds = predictTime.predict_time("mp3", 0)
        self.assertEquals(-1, seconds)

    def test_predict_time_from_filename_not_found(self):
        predictTime = self._get_list()
        seconds = predictTime.predict_time_from_filename("none.txt", "none.txt")
        self.assertEquals(-1, seconds)

    def test_predict_time_multiple(self):
        predictTime = self._get_list()
        predictTime.append("mp3", str(self.MB_BYTES * 10), str(5))
        predictTime.append("mp4", str(self.MB_BYTES * 20), str(20))
        
        seconds_mp3 = predictTime.predict_time("mp3", self.MB_BYTES * 4)
        seconds_mp4 = predictTime.predict_time("mp4", self.MB_BYTES * 4)
        self.assertEquals(2, seconds_mp3)
        self.assertEquals(4, seconds_mp4)
                
if __name__ == '__main__':
    unittest.main()
