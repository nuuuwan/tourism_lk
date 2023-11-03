import os
import shutil

from utils import File, JSONFile, Log

from tlk.parsers.GenericPDF import GenericPDF
from tlk.scrapers.StatisticsPage import DIR_ROOT
from utils_future import SystemMode

log = Log('GenericPDFParser')

DIR_PDFS_PARSED_ROOT = os.path.join('data', 'sltda', 'pdf-parsed')
FORCE_CLEAN = False
TEST_PDF_PATH = os.path.join(
    DIR_ROOT,
    'weekly-tourist-arrivals-reports',
    'tourist-arrivals-2023-october.pdf',
)


class GenericPDFParser:
    @staticmethod
    def get_pdf_paths() -> list[str]:
        for root, _, files in os.walk(DIR_ROOT):
            for file in files:
                if file.endswith('.pdf'):
                    yield os.path.join(root, file)

    @staticmethod
    def build_summary(pdf, dir_pdf_parsed):
        json_path = os.path.join(dir_pdf_parsed, 'summary.json')
        JSONFile(json_path).write(pdf.summary)
        log.debug(pdf.summary)
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
            if len(text.strip()) == 0:
                continue
            lines.append(f'### page {i}')
            lines.append(text)
        File(text_path).write_lines(lines)
        log.debug(f'Wrote {text_path}')

    @staticmethod
    def parse(pdf_path: str):
        log.debug(f'parse({pdf_path})')

        pdf = GenericPDF(pdf_path)

        dir_pdf_parsed = (
            pdf_path.replace(DIR_ROOT, DIR_PDFS_PARSED_ROOT) + '-parsed'
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
        if FORCE_CLEAN:
            if os.path.exists(DIR_PDFS_PARSED_ROOT):
                shutil.rmtree(DIR_PDFS_PARSED_ROOT)
            os.makedirs(DIR_PDFS_PARSED_ROOT)

        pdf_paths = (
            GenericPDFParser.get_pdf_paths()
            if SystemMode.is_prod()
            else [TEST_PDF_PATH]
        )
        for pdf_path in pdf_paths:
            GenericPDFParser.parse_safe(pdf_path)
