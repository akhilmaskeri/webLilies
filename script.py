import sys

from readable import ReadableDocument
from epub import make_epub
from send_mail import MailMan

url = sys.argv[1]

print("creating readable document")
readable_doc = ReadableDocument(url)
title, doc = readable_doc.get_readable_document()

print("makding epub file")
file_name = make_epub(doc, title)

print(f"sending you the file: {file_name}")
mailman = MailMan(
    smtp_server = "smtp.gmail.com",
    port = 587,
    sender_email = "allowed_email_address@your.domain",
    password = "password_for_the_sender_email",
    recipients = "kindle_device_mail_address@kindle.com"
)

mailman.attach_file(file_name)
mailman.send()
