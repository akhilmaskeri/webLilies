import os
import shutil
import uuid
import pathlib
from zipfile import ZipFile
from jinja2 import Template as jinjaTemplate

def make_epub(document, title="article", author="Unknown", imgs=None):

    print(imgs)

    # tmp_name = "/tmp/" + str(uuid.uuid1())
    tmp_name = str(uuid.uuid1())
    
    dirs = [
        tmp_name,
        tmp_name + "/" + "META-INF",
        tmp_name + "/" + "OEBPS",
        tmp_name + "/" + "OEBPS/Styles",
        tmp_name + "/" + "OEBPS/Images"
    ]

    for dir in dirs:
        print(f"making dir: {dir}")
        os.mkdir(dir)

    for img in imgs:
        print(f"moving image {img} to", tmp_name + "/" + "OEBPS/Images")
        shutil.move(img, tmp_name + "/" + "OEBPS/Images")

    shutil.copy("templates/container.xml", tmp_name+"/META-INF/container.xml")

    with open("templates/content.opf", "r") as f:
        content = f.read()
        print(f"passing imgs: {imgs}")
        content_opf = jinjaTemplate(content).render(title=title, author=author, id=tmp_name, imgs=imgs)

        with open(tmp_name+"/OEBPS/content.opf", "w") as content_opf_file:
            content_opf_file.write(content_opf)

    shutil.copy("templates/mimetype", tmp_name+"/mimetype")
    shutil.copy("templates/stylesheet.css", tmp_name+"/OEBPS/Styles/stylesheet.css")

    with open("templates/toc.ncx", "r") as f:
        content = f.read()
        toc_ncx = jinjaTemplate(content).render(title=title, author=author)

        with open(tmp_name+"/OEBPS/toc.ncx", "w") as toc_ncx_file:
            toc_ncx_file.write(toc_ncx)

    with open(tmp_name+"/OEBPS/article.html", "w") as f:
        f.write(document)

    epub_file_name = f"{title}.epub"

    with ZipFile(epub_file_name, mode="w") as archive:    
        archive.write(f"templates/mimetype", arcname="mimetype")
        archive.write(f"{tmp_name}/META-INF/container.xml", arcname="META-INF/container.xml")
        archive.write(f"{tmp_name}/OEBPS/content.opf", arcname="OEBPS/content.opf")
        archive.write(f"{tmp_name}/OEBPS/toc.ncx", arcname="OEBPS/toc.ncx")
        archive.write(f"{tmp_name}/OEBPS", arcname="OEBPS")

        for img in imgs:
            archive.write(f"{tmp_name}/OEBPS/Images/{img}", arcname=f"OEBPS/Images/{img}")

        archive.write(f"{tmp_name}/OEBPS/article.html", arcname="OEBPS/article.html")
        archive.write(f"{tmp_name}/OEBPS/Styles/stylesheet.css", arcname="OEBPS/Styles/stylesheet.css")

    shutil.rmtree(tmp_name)
    return epub_file_name
