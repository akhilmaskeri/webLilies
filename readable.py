import os
import re
import shutil
import requests
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

from readability import Document

valid_tags = [
    "a", "abbr", "acronym", "address", "applet",
    "b", "bdo", "big", "blockquote", "br",
    "body",
    "cite", "code",
    "del", "dfn", "div", "dl",
    "em",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr",
    "html", "head", "title",
    "i", "iframe", "img", "ins",
    "kbd",
    "map",
    "noscript", "ns:svg",
    "object", "ol",
    "p", "pre",
    "q",
    "samp", "script", "small", "span", "strong", "sub", "sup",
    "table", "tt",
    "ul"
]

class ReadableDocument():

    def __init__(self, url):
        self.url = url
        self.split_url = urlsplit(url)
        self.clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

    def download_html(self, url):
        response = requests.get(url)
        doc = Document(response.text)
        return doc

    def download_images(self, soup):

        img_files = []

        imgs = soup.find_all("img", src=True)
        for img in imgs:
            img_src = img["src"]
            file_name = os.path.basename(img_src)
            img_files.append(file_name)
            resp = requests.get(img_src, stream=True)
            if resp.status_code == 200:
                with open(file_name, "wb") as f:
                    shutil.copyfileobj(resp.raw, f)
                    print(f"saved file {file_name}")
                img["src"] = "Images/" + file_name

        return img_files

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

    def validate_tags(self, soup):

        for tag in soup.find_all():
            if tag.name not in valid_tags:
                invalid_tag = soup.find(tag.name)
                invalid_tag.name = "div"
        return soup

    def get_readable_document(self):
        document = self.download_html(self.url)
        article = self.parse_document(document)

        title = article["title"]

        article = article["summary"]
        article = self.fill_empty_href(article)
        article = self.fill_empty_src(article)
        article = self.remove_hex_chars(article)

        soup = BeautifulSoup(article, 'html.parser')

        for img in soup.find_all("img"):
            print(img["src"])

        img_filenames = self.download_images(soup)

        for img in soup.find_all("img"):
            print(img["src"])
        
        if not soup.html.has_attr("xmlns"):
            soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"

        if not soup.html.head:
            head = soup.new_tag("head")
            title_tag = soup.new_tag("title")
            title_tag.string = title
            head.append(title_tag)
            soup.html.body.insert_before(head)

        soup = self.validate_tags(soup)

        return title, soup.prettify(), img_filenames