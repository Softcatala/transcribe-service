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
from email.mime.text import MIMEText


class Sendmail:
    def send(self, text, email):
        try:
            mail_server = os.environ.get("MAIL_SERVER", "mail.scnet")
            mail_port = os.environ.get("MAIL_PORT", 25)
            mail_username = os.environ.get("MAIL_USERNAME", "")
            mail_password = os.environ.get("MAIL_PASSWORD", "")

            port = int(mail_port)
            sender_email = "serveis@softcatala.org"

            with smtplib.SMTP(mail_server, port) as server:
                if len(mail_username) > 0 and len(mail_password) > 0:
                    server.starttls()
                    server.login(mail_username, mail_password)

                message = MIMEMultipart("alternative")
                message["Subject"] = "Servei de transcripció de Softcatalà"
                message["From"] = sender_email
                message["To"] = email

                part = MIMEText(text, "plain")
                message.attach(part)

                server.sendmail(sender_email, email, message.as_string())
        except Exception as e:
            msg = "Error '{0}' sending to {1}".format(e, email)
            logging.error(msg)
