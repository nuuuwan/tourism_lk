import os
import shutil

from utils import File, JSONFile, Log

from tlk.parsers.GenericPDF import GenericPDF
from tlk.scrapers.StatisticsPage import DIR_ROOT
from utils_future import List, SystemMode

log = Log('GenericPDFParser')

DIR_PDFS_PARSED_ROOT = os.path.join('data', 'sltda', 'pdf-parsed')
FORCE_CLEAN = True
TEST_PDF_PATH = os.path.join(
    DIR_ROOT,
    'weekly-tourist-arrivals-reports',
    'tourist-arrivals-2023-october.pdf',
)
MIN_IMAGE_FILE_SIZE = 20_000


class GenericPDFParser:
    @staticmethod
    def get_pdf_paths() -> list[str]:
        pdf_paths = []
        for root, _, files in os.walk(DIR_ROOT):
            for file in files:
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    pdf_paths.append(pdf_path)
        return pdf_paths

    @staticmethod
    def build_summary(pdf, dir_pdf_parsed):
        json_path = os.path.join(dir_pdf_parsed, 'summary.json')
        JSONFile(json_path).write(pdf.summary)
        log.debug(str(pdf.summary))
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
    def build_images(pdf, dir_pdf_parsed):
        dir_images = os.path.join(dir_pdf_parsed, 'images')
        os.makedirs(dir_images, exist_ok=True)

        for i_image, image in enumerate(pdf.images):
            image_path = os.path.join(dir_images, f'image-{i_image}.png')
            image.save(image_path)
            file_size = os.path.getsize(image_path)
            if file_size < MIN_IMAGE_FILE_SIZE:
                os.remove(image_path)
            else:
                log.debug(f'Wrote {image_path}')

    @staticmethod
    def parse(pdf_path: str):
        log.debug(f'parse({pdf_path})')

        dir_pdf_parsed = (
            pdf_path.replace(DIR_ROOT, DIR_PDFS_PARSED_ROOT) + '-parsed'
        )
        if FORCE_CLEAN:
            if os.path.exists(dir_pdf_parsed):
                shutil.rmtree(dir_pdf_parsed)

        if os.path.exists(dir_pdf_parsed):
            log.debug(f'{dir_pdf_parsed} already exists. Skipping.')
            return

        os.makedirs(dir_pdf_parsed, exist_ok=True)

        pdf = GenericPDF(pdf_path)

        GenericPDFParser.build_summary(pdf, dir_pdf_parsed)
        GenericPDFParser.build_tables(pdf, dir_pdf_parsed)
        GenericPDFParser.build_text(pdf, dir_pdf_parsed)
        GenericPDFParser.build_images(pdf, dir_pdf_parsed)

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
        os.makedirs(DIR_PDFS_PARSED_ROOT, exist_ok=True)
        pdf_paths = (
            GenericPDFParser.get_pdf_paths()
            if SystemMode.is_prod()
            else [TEST_PDF_PATH]
        )
        List(pdf_paths).map_parallel(
            GenericPDFParser.parse_safe, max_threads=4
        )
