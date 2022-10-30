import os

import telegram

from db.Database import DeviceIDMap

from engine.arc90doc import Arc90Doc
from engine.epub import Epub
from mailman.send_mail import MailMan

import logging
logger = logging.getLogger("torchd")

class Handle():

    @staticmethod
    def start(bot, update):

        chat_id = update.message.chat.id
        user = update.message.chat.first_name

        logger.info(update)

        message =  "Hello " + user + "!\n\n"
        message += "This bot is developed to enable user to download blogs on kindle app" + "\n"
        message += "Bind your kindle email and send url which appears as a readable document in your kindle app." + "\n\n"
        message += "Wondering how to get kindle email? use this https://www.amazon.in/hz/mycd/digital-console/contentlist/booksAll/" + "\n"
        message += "Preferences > Personal Document Settings > Send-to-Kindle E-Mail Settings"

        bot.send_message(chat_id, text=message)


    @staticmethod
    def bind(bot, update):
        chat_id = update.message.chat.id
        bot.send_message(chat_id, text="bind address", reply_markup=telegram.ForceReply())


    @staticmethod
    def device_id(bot, update, device):
        chat_id = update.message.chat.id

        user_id = update.message.chat.id

        device_id_map = DeviceIDMap()
        device_id_map.set_device_id(user_id, device)

        message = "Gotcha!" + "\n"
        message += "Dont forget to add \"webliliesbot@gmail.com\" to your Approved Personal Document E-mail List" + "\n\n"
        message += "Wondering where to add?" + "\n\n" 
        message += "check here https://www.amazon.in/hz/mycd/myx?ref=myk_mkmw_mig_IN" + "\n\n"
        message += "Preferences > Personal Document Settings > Approved Personal Document E-mail List"
        bot.send_message(chat_id, text=message)


    @staticmethod
    def link(update, links):

        chat_id = update.message.chat.id
        device_id_map = DeviceIDMap()
        device_id = device_id_map.get_device_id(chat_id)

        url = links[0][0] 
        logger.info(f"extracting url: {url}")

        doc = Arc90Doc(url)
        doc.parse()

        logger.info(f"making epub for : {doc.title}")
        epub = Epub(
            url=url,
            title=doc.title,
            content=doc.content,
            author=doc.author
        )

        file_name = epub.save()
        logger.info(f"saved file {file_name}")

        mailman = MailMan(
            smtp_server = "smtp.gmail.com",
            port = 587,
            sender_email = os.environ.get("SENDER_EMAIL"),
            password = os.environ.get("SENDER_PASSWORD"),
            recipients = device_id["device_id"],
        )

        try:
            mailman.attach_file(file_name)
            mailman.send()
            logger.info("mail sent")
        except Exception as e:
            logger.info(e) 

        os.remove(file_name)

    @staticmethod
    def ping(bot, update):
        chat_id = update.message.chat.id
        bot.send_message(chat_id, text="pong")


    @staticmethod
    def help(bot, update):

        help_msg = "This bot is developed to download blogs on your kindle app" + "\n\n"

        help_msg += "Firstly, Bind your kindle email using \\bind" + "\n"
        help_msg += "Wondering where to get kindle email?\ncheck this https://www.amazon.in/hz/mycd/digital-console/contentlist/booksAll/" + "\n"
        help_msg += "Preferences > Personal Document Settings > Send-to-Kindle E-Mail Settings" + "\n\n"

        help_msg += "Secondly, add webliliesbot@gmail.com to your Approved Personal Document E-mail List" + "\n"
        help_msg += "Wondering where to add?" + "\n" 
        help_msg += "check here https://www.amazon.in/hz/mycd/myx?ref=myk_mkmw_mig_IN" + "\n"
        help_msg += "Preferences > Personal Document Settings > Approved Personal Document E-mail List" + "\n\n"

        help_msg += "Finally, send url and if everything goes well, it should appear in your kindle devices"

        chat_id  = update.message.chat.id
        bot.send_message(chat_id, text=help_msg)
