# -*- encoding: utf-8 -*-
#
# Copyright (c) 2022-2025 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from jinja2 import Environment, FileSystemLoader


class Sendmail:
    def _get_mail_server_config(self):
        """Helper method to retrieve mail server configuration from environment variables."""
        mail_server = os.environ.get("MAIL_SERVER", "mail.scnet")
        mail_port = os.environ.get("MAIL_PORT", 25)
        mail_username = os.environ.get("MAIL_USERNAME", "")
        mail_password = os.environ.get("MAIL_PASSWORD", "")
        port = int(mail_port)
        return mail_server, port, mail_username, mail_password

    def _send_email(self, email, subject, message):
        try:
            mail_server, port, mail_username, mail_password = (
                self._get_mail_server_config()
            )
            sender_email = "serveis@softcatala.org"

            with smtplib.SMTP(mail_server, port) as server:
                if mail_username and mail_password:
                    server.starttls()
                    server.login(mail_username, mail_password)

                message["From"] = sender_email
                message["To"] = email
                server.sendmail(sender_email, email, message.as_string())
        except Exception as e:
            msg = f"Error '{e}' sending to {email}"
            logging.error(msg)

    def send(self, text, email):
        """Send a plain text email."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Servei de transcripció de Softcatalà"
            part = MIMEText(text, "plain")
            message.attach(part)
            self._send_email(email, message["Subject"], message)
        except Exception as e:
            msg = f"Error '{e}' sending to {email}"
            logging.error(msg)

    def send_html(self, email, template_name, context):
        try:
            TEMPLATES_DIR = "email-templates"
            env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

            template = env.get_template(f"{template_name}.html")
            html = template.render(context)
            template = env.get_template(f"{template_name}.txt")
            text = template.render(context)

            message = MIMEMultipart("alternative")
            message["Subject"] = "Servei de transcripció de Softcatalà"

            part_text = MIMEText(text, "plain")
            part_html = MIMEText(html, "html")
            message.attach(part_text)
            message.attach(part_html)

            self._send_email(email, message["Subject"], message)
        except Exception as e:
            msg = f"Error '{e}' sending to {email}"
            logging.error(msg)
