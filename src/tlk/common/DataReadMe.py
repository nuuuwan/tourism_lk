import os

from utils import TIME_FORMAT_TIME, File, Log, Time

from utils_future import Link, List

log = Log('DataReadMe')


class DataReadMe:
    @staticmethod
    def update(pdf_link_list: list[Link]):
        time_str = TIME_FORMAT_TIME.stringify(Time.now())
        lines = [
            '# Data (TourismLK)',
            f'*Updated {time_str}*',
            '',
            '## PDFs from [SLTDA](https://www.sltda.gov.lk/statistics)',
            f'*{len(pdf_link_list)} [PDFs](sltda/pdf) scraped*',
        ] + List(pdf_link_list).map(
            lambda link: f'* [{link.text}]({link.local_file_path[5:]})'
        )

        file_path = os.path.join('data', 'README.md')
        File(file_path).write_lines(lines)
        log.info(f'Updated {file_path}')
