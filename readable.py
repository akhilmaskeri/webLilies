import sys
import re
import requests
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

from readability import Document

class ReadableDocument():

    def __init__(self, url):
        self.url = url
        self.split_url = urlsplit(url)
        self.clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

    def download_html(self, url):
        response = requests.get(url)
        doc = Document(response.text)
        return doc

    def parse_document(self, document):
        title = document.title()
        summary = document.summary()

        return {
            "summary": summary,
            "title": title
        }

    def fill_empty_href(self, string):

        scheme = self.split_url.scheme
        netloc = self.split_url.netloc

        pattern = r"""href=(['"])/"""
        replacement = "href=\\1" + scheme + "://" + netloc + "/"

        return re.sub(pattern, replacement, string)

    def remove_hex_chars(self, string):
        return re.sub(r'[^\x00-\x7f]',r'', string)

    def fill_empty_src(self, string):

        scheme = self.split_url.scheme
        netloc = self.split_url.netloc

        pattern = r"""src=(['"])/"""
        replacement = "src=\\1" + scheme + "://" + netloc + "/"

        return re.sub(pattern, replacement, string)

    def get_readable_document(self):
        document = self.download_html(self.url)
        article = self.parse_document(document)

        title = article["title"]

        article = article["summary"]
        article = self.fill_empty_href(article)
        article = self.fill_empty_src(article)
        article = self.remove_hex_chars(article)

        soup = BeautifulSoup(article, 'html.parser')

        if not soup.html.has_attr("xmlns"):
            soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"

        if not soup.html.head:
            head = soup.new_tag("head")
            title_tag = soup.new_tag("title")
            title_tag.string = title
            head.append(title_tag)
            soup.html.body.insert_before(head)

        return title, str(soup)