import os
import shutil

from utils import File, JSONFile, Log

from tlk.parsers.GenericPDF import GenericPDF
from tlk.scrapers.StatisticsPage import DIR_ROOT, LIMIT

log = Log('GenericPDFParser')

DIR_PDFS_PARSED_ROOT = os.path.join('data', 'sltda', 'pdf-parsed')


class GenericPDFParser:
    @staticmethod
    def get_pdf_paths() -> list[str]:
        for root, dirs, files in os.walk(DIR_ROOT):
            for file in files:
                if file.endswith('.pdf'):
                    yield os.path.join(root, file)

    @staticmethod
    def build_summary(pdf, dir_pdf_parsed):
        json_path = os.path.join(dir_pdf_parsed, 'summary.json')
        JSONFile(json_path).write(pdf.summary)
        log.debug(f'Wrote {json_path}')

    @staticmethod
    def build_tables(pdf, dir_pdf_parsed):
        for i_table, table in enumerate(pdf.tables):
            table_path = os.path.join(dir_pdf_parsed, f'table-{i_table}.csv')
            table.df.to_csv(table_path, index=False)
            log.debug(f'Wrote {table_path}')

    @staticmethod
    def build_text(pdf, dir_pdf_parsed):
        text_path = os.path.join(dir_pdf_parsed, 'text.md')
        lines = []
        for i, text in enumerate(pdf.text_list):
            lines.append(f'### page {i}')
            lines.append(text)
        File(text_path).write_lines(lines)
        log.debug(f'Wrote {text_path}')

    @staticmethod
    def parse(pdf_path: str):
        log.debug(f'parse({pdf_path})')

        pdf = GenericPDF(pdf_path)

        dir_pdf_parsed = os.path.join(
            DIR_PDFS_PARSED_ROOT, os.path.basename(pdf_path) + '-parsed'
        )
        os.makedirs(dir_pdf_parsed)

        GenericPDFParser.build_summary(pdf, dir_pdf_parsed)
        GenericPDFParser.build_tables(pdf, dir_pdf_parsed)
        GenericPDFParser.build_text(pdf, dir_pdf_parsed)

    @staticmethod
    def parse_safe(pdf_path: str):
        try:
            GenericPDFParser.parse(pdf_path)
        except Exception as e:
            log.error(f'Failed to parse {pdf_path}: {e}')

    @staticmethod
    def parse_all():
        if os.path.exists(DIR_PDFS_PARSED_ROOT):
            shutil.rmtree(DIR_PDFS_PARSED_ROOT)
        os.makedirs(DIR_PDFS_PARSED_ROOT)

        for i, pdf_path in enumerate(GenericPDFParser.get_pdf_paths()):
            GenericPDFParser.parse_safe(pdf_path)
            if i >= LIMIT:
                break
