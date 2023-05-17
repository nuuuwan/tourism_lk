import country_converter
from utils import TSVFile

MOST_POPULAR_COUNTRY_LIST = [
    'IND',
    'GBR',
    'CHN',
    'DEU',
    'RUS',
    'FRA',
    'AUS',
    'USA',
    'MDV',
    'CAN',
    'NLD',
    'UKR',
    'ITA',
    'JPN',
    'CHE',
    'ESP',
    'POL',
    'SWE',
    'SAU',
    'CZE',
]


def build_country_to_region():
    d_list = TSVFile('data/arrivals-by-country/country_info.tsv').read()
    return {d['alpha3']: d['sub_region'] for d in d_list}


COUNTRY_TO_REGION = build_country_to_region()


def find_country(search_key):
    return country_converter.convert(names=[search_key], to='ISO3')


def find_sub_region(country_name):
    return COUNTRY_TO_REGION.get(country_name, 'unknown')


if __name__ == '__main__':
    print(find_country('Sri Lanka'))
    print(find_sub_region('LKA'))
