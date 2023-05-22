# -*- encoding: utf-8 -*-
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

import numpy as np

class SimilarUsers:
    def _levenshtein(self, seq1, seq2):
        size_x = len(seq1) + 1
        size_y = len(seq2) + 1
        matrix = np.zeros((size_x, size_y))
        for x in range(size_x):
            matrix[x, 0] = x
        for y in range(size_y):
            matrix[0, y] = y

        for x in range(1, size_x):
            for y in range(1, size_y):
                if seq1[x - 1] == seq2[y - 1]:
                    matrix[x, y] = min(
                        matrix[x - 1, y] + 1, matrix[x - 1, y - 1], matrix[x, y - 1] + 1
                    )
                else:
                    matrix[x, y] = min(
                        matrix[x - 1, y] + 1,
                        matrix[x - 1, y - 1] + 1,
                        matrix[x, y - 1] + 1,
                    )
        return matrix[size_x - 1, size_y - 1]

    def get_count_of_files_for_similar_users(self, email_list, user_email):
        MIN_LEN = 5
        found = 0
        found_emails = []

        user = user_email.split("@")[0]
        if len(user) < MIN_LEN:
            return found, found_emails

        emails_to_files = {
            email: sum(1 for inner_email in email_list if email == inner_email)
            for email in email_list
        }
        for email in emails_to_files:
            count = emails_to_files[email]

            user_record = email.split("@")[0]
            if len(user_record) < MIN_LEN:
                continue

            score = self._levenshtein(user.lower(), user_record.lower())
            normalized_score = score / min(len(user), len(user_record))
            if normalized_score < 0.30:
                found += count
                found_emails.append(email)

        return found, found_emails
