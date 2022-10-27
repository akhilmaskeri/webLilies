import os
import shutil
import requests
from urllib.parse import urlsplit

from readability import Document

class Arc90Doc():

    def __init__(self, url):
        self.url = url
        self.split_url = urlsplit(url)

        self.html = None

        self.title = None
        self.author = None
        self.content = None

        self.get_html()
        
    def get_html(self):
        response = requests.get(self.url)
        self.html = response.text
    
    def parse(self):
        document = Document(self.html)

        self.title = document.title()
        self.author = self.split_url.netloc
        self.content = document.summary()
        