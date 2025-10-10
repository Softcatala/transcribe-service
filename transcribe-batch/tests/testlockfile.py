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

from lockfile import LockFile
import unittest
import tempfile


class TestLockFile(unittest.TestCase):
    def test_create(self):
        filename = tempfile.NamedTemporaryFile().name
        result = LockFile(filename).create()
        self.assertEqual(True, result)

    def test_create_locked_by_other_process(self):
        filename = tempfile.NamedTemporaryFile().name
        LockFile(filename).create()
        result = LockFile(filename).create()
        self.assertEqual(False, result)

    def test_has_lock(self):
        filename = tempfile.NamedTemporaryFile().name
        lockfile = LockFile(filename)
        lockfile.create()
        self.assertEqual(True, lockfile.has_lock())

    def test_has_delete(self):
        filename = tempfile.NamedTemporaryFile().name
        lockfile = LockFile(filename)
        lockfile.create()
        lockfile.delete()
        self.assertEqual(False, lockfile.has_lock())


if __name__ == "__main__":
    unittest.main()
