from functools import cached_property

import camelot
import fitz
from PyPDF2 import PdfReader

from utils_future import List


class GenericPDF:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    @cached_property
    def summary(self) -> dict:
        return dict(
            pdf_path=self.pdf_path,
            n_pages=self.n_pages,
            n_tables=self.n_tables,
            n_images=self.n_images,
        )

    # PyPDF2
    @cached_property
    def pdf_reader(self):
        return PdfReader(self.pdf_path)

    @cached_property
    def n_pages(self) -> int:
        reader = self.pdf_reader
        return len(reader.pages)

    @cached_property
    def pages(self) -> list:
        return self.pdf_reader.pages

    @cached_property
    def text_list(self) -> list[str]:
        return List(self.pages).map(lambda page: page.extractText())

    # camelot-py
    @cached_property
    def tables(self):
        return camelot.read_pdf(
            self.pdf_path,
            pages="all",
            flavor='stream',
            strip_text='\n',
        )

    @cached_property
    def n_tables(self):
        return len(self.tables)

    # pymupdf
    @cached_property
    def images(self):
        doc = fitz.open(self.pdf_path)
        n_pages = len(doc)
        images = []
        for i_page in range(n_pages):
            page = doc[i_page]
            page_images = page.get_images()
            for image in page_images:
                xref = image[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                images.append(pix)
        return images

    @cached_property
    def n_images(self):
        return len(self.images)
