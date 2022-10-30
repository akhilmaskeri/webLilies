import os
import re
import requests

from datetime import datetime

from flask import Flask, request
import telegram

from handler.handler import Handle

from constants import TOKEN, USERNAME, URL
import logging

log_format = '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'

logging.basicConfig(filename="xapp.log", level=logging.DEBUG, format=log_format)
logger = logging.getLogger("torchd")

app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def repsond():

    update = telegram.Update.de_json(request.get_json(force=True), bot)
    print(update)
    try:
        chat_id = update.message.chat.id
        msg_id = update.message.message_id
    except:
        return 'ok'

    text = update.message.text.encode('utf-8').decode()
    logger.info(f"recieved text: {text}")

    if text == "/start":
        logger.info("handling start")
        Handle.start(bot, update)

    if text == "/ping":
        logger.info("handling ping")
        Handle.ping(bot, update)

    if text == "/bind":
        logger.info("handling bind")
        Handle.bind(bot, update)

    if text == "/help":
        logger.info("handling help")
        Handle.help(bot, update)

    if update.message.reply_to_message:

        print(update.message.reply_to_message)

        if update.message.reply_to_message.text == "bind address":
            print("bind address")
            device_id_value = update.message.text

            device_id_regex = r"[\w_-]+@kindle.com"
            device_id = re.findall(device_id_regex, device_id_value)

            if device_id:
                logger.info("handling device id")
                Handle.device_id(bot, update, device_id[0])

    link_regex = re.compile("((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", re.DOTALL) 
    links = re.findall(link_regex, text)

    if links:
        Handle.link(update, links)

    return "ok"


@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(stream_handler)

    context = ("keys/fullchain.pem", "keys/privkey.pem")

    app.run(
        threaded=True,
        host="0.0.0.0",
        port=443,
        ssl_context=context,
        debug=True,
    )

