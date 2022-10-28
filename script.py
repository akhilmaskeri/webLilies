import sys
from engine.arc90doc import Arc90Doc
from engine.epub import Epub
from mailman.send_mail import MailMan

url = sys.argv[1]

doc = Arc90Doc(url)
doc.parse()

epub = Epub(
  url=url,
  title=doc.title,
  content=doc.content,
  author=doc.author
)

file_name = epub.save(path=".")

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
