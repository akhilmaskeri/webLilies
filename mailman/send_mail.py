from fileinput import filename
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import logging
logger = logging.getLogger("torchd")

import traceback

class MailMan():

    def __init__(self, smtp_server, port, sender_email, password, recipients=[]):

        self.smtp_server = smtp_server
        self.port = port
        self.sender_email = sender_email
        self.password = password
        self.recipients_list = recipients

        self.message = MIMEMultipart("alternative")

    def attach_file(self, file_name:str = None):

        logger.info(f"attaching file: {file_name}")

        with open(file_name, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={file_name}",
        )

        # Add attachment to message and convert message to string
        self.message.attach(part)

    def send(self):

        try:
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender_email, self.password)

        except Exception as e:
            logger.info(traceback.format_exc())

        if True:
            recipients = ""

            logger.info("recipients %s", self.recipients_list)
            
            if type(self.recipients_list) == str:
                recipients = self.recipients_list
            else:
                recipients = ",".join(self.recipients_list)

            self.message["To"] = recipients

        try:

            logger.info("sender : %s", self.sender_email)
            server.sendmail(
                self.sender_email,
                recipients,
                self.message.as_string()
            )
            server.close() 
        except Exception as e:
            logger.info(traceback.format_exc())
