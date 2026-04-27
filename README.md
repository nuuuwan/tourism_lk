# Tourism LK

An automated pipeline for scraping, parsing, and structuring Sri Lanka Tourism data from the [Sri Lanka Tourism Development Authority (SLTDA)](https://www.sltda.gov.lk/statistics).

## Overview

This project aims to convert unstructured PDF reports from SLTDA into machine-readable formats (CSV, JSON, Markdown) to facilitate analysis and visualization of tourism trends in Sri Lanka. It handles various report types, including weekly, monthly, and annual statistical reports.

## Key Features

- **Automated Scraping:** Discovers and downloads the latest PDF reports from the SLTDA statistics page.
- **Robust PDF Parsing:**
  - **Tables:** Extracted as CSV files using `camelot-py`.
  - **Text:** Extracted as Markdown files for easy reading and searching.
  - **Images:** Extracted as PNG files (filtered by size to remove icons/junk).
  - **Metadata:** Extraction summaries (page count, table count, etc.) saved as JSON.
- **Daily Updates:** Integrated with GitHub Actions to run the pipeline daily and keep the data synchronized.

## Directory Structure

- `src/tlk/`: Core logic of the application.
  - `scrapers/`: Logic for web scraping and file downloading.
  - `parsers/`: PDF processing and data extraction logic.
  - `common/`: Shared utilities and data documentation generators.
- `workflows/`: Orchestration scripts for the data pipeline.
- `data/sltda/`:
  - `pdf/`: Raw PDF files organized by report type.
  - `pdf-parsed/`: Extracted data in structured formats, mirroring the PDF directory structure.
- `.github/workflows/`: GitHub Actions configuration for the daily pipeline.
- `__archive/`: Legacy code and experimental analysis (including ML models and charts).

## Installation

### Prerequisites

- Python 3.10+
- System dependencies for PDF processing (required by `camelot-py` and `pdf2image`):
  ```bash
  sudo apt update
  sudo apt install ghostscript poppler-utils
  ```

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/nuuuwan/tourism_lk.git
   cd tourism_lk
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the entire pipeline (scrape + parse + update registry):

```bash
export PYTHONPATH="$PYTHONPATH:./src"
python workflows/pipeline.py
```

### Individual Steps

- **Scrape:** `python workflows/scrape.py` (Downloads new PDFs)
- **Parse:** `python workflows/parse.py` (Processes PDFs into CSV/JSON/MD)
- **Post-Process:** `python workflows/post_process.py` (Placeholder for future data refinement)

## Data Output

Parsed data is located in `data/sltda/pdf-parsed/`. For each PDF file, a directory is created containing:
- `summary.json`: Metadata about the extraction (number of pages, tables, images).
- `text.md`: Extracted text organized by page.
- `tables/`: Directory containing extracted tables as `table-N.csv`.
- `images/`: Directory containing extracted images/charts as `image-N.png`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
