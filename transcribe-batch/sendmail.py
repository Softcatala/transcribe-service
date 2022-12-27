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

import smtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText


class Sendmail():

    def _get_attachment_part(self, filename):
        with open(filename, mode='rb') as file:
            content = file.read()

        attachment_name = os.path.basename(filename)          
        part = MIMEApplication(content, Name=attachment_name)
        part['Content-Disposition'] = f'attachment; filename={attachment_name}'
        return part

    def _get_body_part(self, body_text_file):
        with open(body_text_file, encoding='utf-8', mode='r') as file:
            file_text = file.read()

        body_text = "Aquí teniu la transcripció que heu demanat com a text. Com a adjunt teniu el fitxer amb les marques de temps amb format srt.\n\n\n"
        body_text += file_text
        part = MIMEText(body_text, "plain")
        return part


    def send(self, body_text_file, email, attachment):
 #       try:
        port = 25
        sender_email = "info@softcatala.org"

        with smtplib.SMTP("mail.scnet", port) as server:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Transcripció de Softcatalà"
            message["From"] = sender_email
            message["To"] = email

            if attachment:
                body = self._get_body_part(body_text_file)
                message.attach(body)
                                
                part = self._get_attachment_part(attachment)
                message.attach(part)
            else:
                body = self._get_body_part(body_text_file)
                message.attach(body)

            server.sendmail(sender_email, email, message.as_string())
#        except Exception as e:
#            msg = "Error '{0}' sending to {1}".format(e, email)
#            logging.error(msg)

