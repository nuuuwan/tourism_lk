import os

from utils import TIME_FORMAT_TIME, File, Log, Time

from utils_future import Link, List

log = Log('DataReadMe')


class DataReadMe:
    @staticmethod
    def get_pdf_lines(pdf_link_list):
        def get_link_line(link: Link):
            path = link.local_file_path[5:]
            label = link.local_file_path[15:]
            parsed_path = path.replace('.pdf', '.pdf-parsed')
            return f'* [{label}]({path}) ([parsed]({parsed_path}))'

        inner_lines = List(pdf_link_list).map(get_link_line)
        return [
            '## PDFs from [SLTDA](https://www.sltda.gov.lk/statistics)',
            f'*{len(pdf_link_list)} [PDFs](sltda/pdf) scraped*',
        ] + inner_lines

    @staticmethod
    def update(pdf_link_list: list[Link]):
        time_str = TIME_FORMAT_TIME.stringify(Time.now())
        pdf_link_list = sorted(pdf_link_list, key=lambda x: x.local_file_path)
        lines = [
            '# Data (TourismLK)',
            f'*Updated {time_str}*',
            '',
        ] + DataReadMe.get_pdf_lines(pdf_link_list)

        file_path = os.path.join('data', 'README.md')
        File(file_path).write_lines(lines)
        log.info(f'Updated {file_path}')
