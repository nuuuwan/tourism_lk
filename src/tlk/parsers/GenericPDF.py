from functools import cached_property

import camelot
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
        return camelot.read_pdf(self.pdf_path, pages="all")

    @cached_property
    def n_tables(self):
        return len(self.tables)
