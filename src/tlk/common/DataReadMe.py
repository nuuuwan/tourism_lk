import os

from utils import TIME_FORMAT_TIME, File, Log, Time

log = Log('DataReadMe')


class DataReadMe:
    @staticmethod
    def update(n_pdf_links: int):
        time_str = TIME_FORMAT_TIME.stringify(Time.now())
        lines = [
            '# Data (TourismLK)',
            f'*Updated {time_str}*',
            '',
            '## PDF Scraping',
            f'* {n_pdf_links} [links](data/sltda/pdf) scraped',
        ]
        file_path = os.path.join('data', 'README.md')
        File(file_path).write_lines(lines)
        log.info(f'Updated {file_path}')
