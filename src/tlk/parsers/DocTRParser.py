import os
import shutil
from utils import File, Log
from tlk.parsers.GenericPDF import GenericPDF
from tlk.scrapers.StatisticsPage import DIR_ROOT
from utils_future import List, SystemMode

import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

log = Log('DocTRParser')

DIR_PDFS_PARSED_OCR_ROOT = os.path.join('data', 'sltda', 'pdf-parsed-doctr')
FORCE_CLEAN = False
TEST_PDF_PATH = os.path.join(
    DIR_ROOT,
    'weekly-tourist-arrivals-reports',
    'tourist-arrivals-2023-october.pdf',
)

class DocTRParser:
    _predictor = None

    @classmethod
    def get_predictor(cls):
        if cls._predictor is None:
            log.info("Loading docTR model...")
            cls._predictor = ocr_predictor(pretrained=True)
            if torch.cuda.is_available():
                log.info("Moving docTR model to GPU...")
                cls._predictor = cls._predictor.cuda()
        return cls._predictor

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
    def parse(pdf_path: str):
        log.info(f'DocTR parse({pdf_path})')

        dir_pdf_parsed = (
            pdf_path.replace(DIR_ROOT, DIR_PDFS_PARSED_OCR_ROOT) + '-parsed'
        )
        
        if FORCE_CLEAN and os.path.exists(dir_pdf_parsed):
            shutil.rmtree(dir_pdf_parsed)

        if os.path.exists(dir_pdf_parsed):
            log.debug(f'{dir_pdf_parsed} already exists. Skipping.')
            return

        os.makedirs(dir_pdf_parsed, exist_ok=True)
        
        try:
            # Load the PDF file directly via docTR
            doc = DocumentFile.from_pdf(pdf_path)
        except Exception as e:
            log.error(f'Failed to read PDF with docTR {pdf_path}: {e}')
            return

        predictor = DocTRParser.get_predictor()
        
        text_path = os.path.join(dir_pdf_parsed, 'ocr-text.md')
        lines = []
        
        log.debug(f'Running OCR on {len(doc)} pages of {pdf_path}...')
        try:
            result = predictor(doc)
            
            for i, page in enumerate(result.pages):
                lines.append(f'### page {i}')
                page_text = []
                for block in page.blocks:
                    for line in block.lines:
                        line_text = " ".join([word.value for word in line.words])
                        page_text.append(line_text)
                lines.append("\n".join(page_text))
                lines.append("") # Empty line for spacing
                
            File(text_path).write_lines(lines)
            log.info(f'Wrote {text_path}')
        except Exception as e:
            log.error(f'Failed during OCR prediction for {pdf_path}: {e}')

    @staticmethod
    def parse_safe(pdf_path: str):
        try:
            DocTRParser.parse(pdf_path)
        except Exception as e:
            log.error(f'Failed to DocTR parse {pdf_path}: {e}')

    @staticmethod
    def parse_all():
        os.makedirs(DIR_PDFS_PARSED_OCR_ROOT, exist_ok=True)

        pdf_paths = (
            DocTRParser.get_pdf_paths()
            if SystemMode.is_prod()
            else [TEST_PDF_PATH]
        )
        # DocTR processes documents reasonably fast on GPU, sequence is fine
        for pdf_path in pdf_paths:
            DocTRParser.parse_safe(pdf_path)
