import os
import re
import shutil
import uuid
import requests
from urllib.parse import urlsplit

from zipfile import ZipFile
from bs4 import BeautifulSoup
from jinja2 import Template

import logging
logger = logging.getLogger("torchd")

class Epub():

    EPUB_VALID_TAGS  = [
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
    
    def __init__(self, title, author, content, url):
        self.url = url
        self.title = title
        self.author = author
        self.content = content
        self.soup = None
        self.images = []

        self.split_url = urlsplit(url)
        

    def download_images(self, path="."):

        images = self.soup.find_all("img")
        for img in images:
            src = img["src"]
            file_name = os.path.basename(src)

            if "?" in file_name:
                file_name = file_name.split("?")[0]

            self.images.append(file_name)
            try:
                resp = requests.get(src, stream=True, timeout=7)

                if resp.status_code == 200:
                    with open(file_name, "wb") as img_file:
                        shutil.copyfileobj(resp.raw, img_file)

            except requests.exceptions.ConnectTimeout:
                logger.info(f"connection timedout for {src}")
                # remove the object from soup
                img.decompose()
                self.images.pop()


    def replace_empty_links(self):
        """
            if domain to links that has omitted it
        """

        scheme = self.split_url.scheme
        netloc = self.split_url.netloc

        pattern = r"""href=(['"])/"""
        replacement = "href=\\1" + scheme + "://" + netloc + "/"

        new_content = re.sub(pattern, replacement, self.content)
        self.content = new_content

    
    def remove_hex_characters(self):
        """
            remove hex content if present
        """
        new_content = re.sub(r'[^\x00-\x7f]', r'', self.content)
        self.content = new_content


    def replace_invalid_tags(self):
        for tag in self.soup.find_all():
            if tag.name not in self.EPUB_VALID_TAGS:
                invalid_tag = self.soup.find(tag.name)
                invalid_tag.name = "div"


    def make(self):
        self.replace_empty_links()
        self.remove_hex_characters()

        self.soup = BeautifulSoup(self.content, 'html.parser')
        self.soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"

        if not self.soup.html.head:
            title_tag = self.soup.new_tag("title")
            title_tag.string = self.title
            head_tag = self.soup.new_tag("head")
            head_tag.append(title_tag)
            self.soup.html.body.insert_before(head_tag)

        heading = self.soup.new_tag("h1")
        heading.string = self.title
        self.soup.html.body.insert(position=0, new_child=heading)

        article_url = self.soup.new_tag("a")
        article_url.string = "Read Original Article here."
        article_url["href"] = self.url

        original_article_link = self.soup.new_tag("small")
        original_article_link.append(article_url)

        self.soup.html.body.insert(position=1, new_child=original_article_link)

        self.replace_invalid_tags()


    def save(self, path="."):

        self.make()
        self.download_images(path)

        epub_file_name = f"{self.title}.epub"
        tmp_name = str(uuid.uuid1())

        META_INF = tmp_name + "/" + "META-INF"
        OEBPS = tmp_name + "/" + "OEBPS"
        STYLES = tmp_name + "/" + "OEBPS/Styles"
        IMAGES = tmp_name + "/" + "OEBPS/Images"


        with ZipFile(epub_file_name, mode="w") as archive:

            archive.write(f"templates/mimetype", arcname="mimetype")
            archive.write(f"templates/container.xml", arcname="META-INF/container.xml")
            archive.write(f"templates/stylesheet.css", arcname="OEBPS/Styles/stylesheet.css")

            for dir in [tmp_name, META_INF, OEBPS, STYLES, IMAGES]:
                os.mkdir(dir)

            with open("templates/content.opf", "r") as f:
                content = f.read()
                content_opf = Template(content).render(
                    title=self.title,
                    author=self.author,
                    id=tmp_name,
                    imgs=self.images
                )
                archive.writestr("OEBPS/content.opf", content_opf)

            with open("templates/toc.ncx", "r") as f:
                content = f.read()
                toc_ncx = Template(content).render(
                    title=self.title,
                    author=self.author
                )
                archive.writestr("OEBPS/toc.ncx", toc_ncx)

            archive.writestr("OEBPS/article.html", self.soup.prettify())

            for img in self.images:
                try:
                    shutil.move(img, IMAGES)
                    archive.write(f"{IMAGES}/{img}", arcname=f"OEBPS/Images/{img}")
                except shutil.Error:
                    logger.info("Error moving image file")

        shutil.rmtree(tmp_name)
        return epub_file_name
