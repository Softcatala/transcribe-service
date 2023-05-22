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

from similarusers import SimilarUsers
import unittest

class TestSimilarUsers(unittest.TestCase):

    def test_does_user_has_max_files_in_queue_short_email(self):
       similar_users = SimilarUsers()
       email_list = ["jmas@softcatala.org", "jmas@softcatala.org", "jmas@softcatala.org", "jmas@softcatala.cat"]
       result, emails = similar_users.get_count_of_files_for_similar_users(email_list, "jmas@softcatala.org")
       self.assertEquals(0, result)

    def test_does_user_has_max_files_in_almost_similar(self):
       similar_users = SimilarUsers()
       email_list = ["jordi.massana@gmail.com", "jordi.massana@gmail.com", "jordi.mas@gmail.com", "jordi.mas@gmail.com"]
       result, emails = similar_users.get_count_of_files_for_similar_users(email_list, "jordi.mas@gmail.com")
       self.assertEquals(2, result)

    def test_does_user_has_max_files_in_same_user_name(self):
       similar_users = SimilarUsers()
       email_list = ["jordi.mas@softcatala.org", "jordi.mas@softcatala.org", "jordi.mas@softcatala.cat", "jordi.mas@softcatala.cat"]
       result, emails = similar_users.get_count_of_files_for_similar_users(email_list, "jordi.mas@softcatala.cat")
       self.assertEquals(4, result)

    def test_does_user_has_max_files_in_simiar_user_name(self):
       similar_users = SimilarUsers()
       email_list = ["jordi.mas11@softcatala.org", "jordi.mas22@softcatala.org", "jordi.mas@softcatala.cat", "jordi.mas@softcatala.cat"]
       result, emails = similar_users.get_count_of_files_for_similar_users(email_list, "jordi.mas@softcatala.cat")
       self.assertEquals(4, result)

if __name__ == '__main__':
    unittest.main()
