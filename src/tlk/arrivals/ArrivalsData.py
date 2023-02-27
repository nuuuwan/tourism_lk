from dataclasses import dataclass

from utils import Time, TimeFormat, TSVFile

TSV_FILE_PATH = "data/sri_lanka.tourism.arrivals.by_month.tsv"


@dataclass
class ArrivalsData:
    ut: int
    arrivals: int

    @property
    def t(self):
        return Time(self.ut)

    @property
    def date(self):
        return TimeFormat('%Y-%m').stringify(self.t)

    @staticmethod
    def from_dict(d):
        ut = TimeFormat('%Y-%m-%d').parse(d['month']).ut
        return ArrivalsData(
            ut=ut,
            arrivals=(int)(d["arrivals"]),
        )

    @staticmethod
    def from_file():
        return [
            ArrivalsData.from_dict(data)
            for data in TSVFile(TSV_FILE_PATH).read()
        ]


if __name__ == '__main__':
    print(ArrivalsData.from_file())
