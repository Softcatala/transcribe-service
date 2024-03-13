# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from execution import Execution
import unittest
import tempfile


class TestExecution(unittest.TestCase):
    def test_get_transcription_language_short_text(self):
        with tempfile.NamedTemporaryFile(mode="w") as temp_file:
            text = "Short text"
            temp_file.write(text)
            temp_file.flush()

            execution = Execution(threads=4)
            language = execution.get_transcription_language(temp_file.name)
            self.assertEquals("ca", language)

    def test_get_transcription_language_long_english(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=True) as temp_file:
            text = '"Montserrat" literally means "serrated (like the common handsaw) mountain" in Catalan. It describes its peculiar aspect with a multitude of rock formations that are visible from a great distance. The mountain is composed of strikingly pink conglomerate, a form of sedimentary rock. Montserrat was designated as a National Park in 1987. The Monastery of Montserrat which houses the virgin that gives its name to the monastery is also on the mountain, although it is also known as La Moreneta ("the little tan/dark one" in Catalan).'
            temp_file.write(text)
            temp_file.flush()
            execution = Execution(threads=4)
            language = execution.get_transcription_language(temp_file.name)
            self.assertEquals("en", language)

    def test_get_transcription_language_long_catalan(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=True) as temp_file:
            text = "Montserrat és un massís muntanyós de Catalunya, situada a cavall de les comarques del Bages, l'Anoia i el Baix Llobregat. És força prominent i té un paper destacat en la tradició catalana, entre altres motius gràcies a una geologia i una topografia pròpies molt característiques que han estat valorades estèticament de manera positiva. S'hi aixeca el monestir de Montserrat, una abadia benedictina consagrada a la Mare de Déu de Montserrat: una marededéu trobada, i també coneguda popularment amb el nom de “la Moreneta”. Així mateix hi ha el Monestir de Sant Benet de Montserrat que és de monges benedictines."
            temp_file.write(text)
            temp_file.flush()
            execution = Execution(threads=4)
            language = execution.get_transcription_language(temp_file.name)
            self.assertEquals("ca", language)

if __name__ == "__main__":
    unittest.main()
