import os
import shutil
import base64
import requests
import io
import time
from PIL import Image
from utils import File, Log
from tlk.parsers.GenericPDF import GenericPDF
from tlk.scrapers.StatisticsPage import DIR_ROOT
from utils_future import List, SystemMode

log = Log('GLMOCRParser')

DIR_PDFS_PARSED_OCR_ROOT = os.path.join('data', 'sltda', 'pdf-parsed-ocr')
FORCE_CLEAN = False
TEST_PDF_PATH = os.path.join(
    DIR_ROOT,
    'weekly-tourist-arrivals-reports',
    'tourist-arrivals-2023-october.pdf',
)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "glm-ocr"
MAX_RETRIES = 3
RETRY_DELAY = 5
MAX_IMAGE_SIZE = (1024, 1024) # Resize to fit within 1024x1024

class GLMOCRParser:
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
    def prepare_image(image):
        # Resize image if it exceeds MAX_IMAGE_SIZE
        if image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]:
            image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (JPEG doesn't support RGBA)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    @staticmethod
    def ocr_image(image):
        base64_image = GLMOCRParser.prepare_image(image)
        payload = {
            "model": MODEL_NAME,
            "prompt": "OCR the following image and return the text in markdown format.",
            "images": [base64_image],
            "stream": False,
            "options": {
                "num_thread": 8 # Use multiple threads for preprocessing
            }
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(OLLAMA_API_URL, json=payload, timeout=300) # Increased timeout for GPU/Vision processing
                response.raise_for_status()
                return response.json().get('response', '')
            except Exception as e:
                log.error(f"Ollama API error (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    return f"[OCR Error: {e}]"
        return ""

    @staticmethod
    def parse(pdf_path: str):
        log.info(f'GLM-OCR parse({pdf_path})')

        dir_pdf_parsed = (
            pdf_path.replace(DIR_ROOT, DIR_PDFS_PARSED_OCR_ROOT) + '-parsed'
        )
        
        if FORCE_CLEAN and os.path.exists(dir_pdf_parsed):
            shutil.rmtree(dir_pdf_parsed)

        if os.path.exists(dir_pdf_parsed):
            log.debug(f'{dir_pdf_parsed} already exists. Skipping.')
            return

        os.makedirs(dir_pdf_parsed, exist_ok=True)
        
        pdf = GenericPDF(pdf_path)
        try:
            images = pdf.images 
        except Exception as e:
            log.error(f'Failed to extract images from {pdf_path}: {e}')
            return

        text_path = os.path.join(dir_pdf_parsed, 'ocr-text.md')
        lines = []
        
        for i, image in enumerate(images):
            log.debug(f'Processing page {i} of {pdf_path}')
            ocr_text = GLMOCRParser.ocr_image(image)
            lines.append(f'### page {i}')
            lines.append(ocr_text)
            time.sleep(1) # Delay between pages
            
        File(text_path).write_lines(lines)
        log.info(f'Wrote {text_path}')

    @staticmethod
    def parse_safe(pdf_path: str):
        try:
            GLMOCRParser.parse(pdf_path)
        except Exception as e:
            log.error(f'Failed to OCR parse {pdf_path}: {e}')

    @staticmethod
    def parse_all():
        os.makedirs(DIR_PDFS_PARSED_OCR_ROOT, exist_ok=True)

        pdf_paths = (
            GLMOCRParser.get_pdf_paths()
            if SystemMode.is_prod()
            else [TEST_PDF_PATH]
        )
        for pdf_path in pdf_paths:
            GLMOCRParser.parse_safe(pdf_path)
