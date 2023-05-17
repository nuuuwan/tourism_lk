import os

from utils import CSVFile, Log, String, TSVFile

from tlk.countries.Country import find_country

YEAR_LIST = [2018, 2019, 2020, 2021, 2022, 2023]
ALL_TSV_PATH = os.path.join('data', 'arrivals-by-country', 'all.tsv')
ALL_BY_MONTH_PATH = os.path.join(
    'data', 'arrivals-by-country', 'all-by-month.tsv'
)
ALL_BY_REGION = os.path.join(
    'data', 'arrivals-by-country', 'all-by-region.tsv'
)

log = Log('arrivals-by-country')


def clean(d, year):
    items = list(d.items())
    country_raw = items[1][1]
    country = find_country(country_raw)
    if country is None:
        print(country_raw)

    d_new = dict(
        country=country,
        year=year,
    )
    n_months = 12
    for i_month in range(n_months):
        month = i_month + 1
        month_str = f'month-{month:02d}'
        if len(items) > 2 + i_month:
            v = String(items[2 + i_month][1]).int
        else:
            v = 0
        d_new[month_str] = v
    return d_new


def clean_data():
    all_d_list = []
    for year in YEAR_LIST:
        csv_path = os.path.join(
            'data',
            'arrivals-by-country',
            f'[sltda] arrivals-by-country-{year}.csv',
        )
        raw_d_list = CSVFile(csv_path).read()
        cleaned_d_list = [clean(d, year) for d in raw_d_list]
        n = len(cleaned_d_list)
        log.debug(f'Found {n} countries for {year}')
        all_d_list += cleaned_d_list

    TSVFile(ALL_TSV_PATH).write(all_d_list)
    log.info(f'Saved {ALL_TSV_PATH}')


def by_month():
    all_d_list = TSVFile(ALL_TSV_PATH).read()
    idx = {}
    country_set = set()
    for d in all_d_list:
        country = d['country']
        country_set.add(country)
        if country not in idx:
            idx[country] = {}
        year = String(d['year']).int
        for i_month in range(12):
            month = i_month + 1
            month_str = f'month-{month:02d}'
            value = String(d[month_str]).int
            complete_month = f'{year}-{month:02d}-15'
            idx[country][complete_month] = value

    d_list = []
    for country in sorted(country_set):
        d = dict(country=country)
        for year in YEAR_LIST:
            for i_month in range(12):
                month = i_month + 1
                complete_month = f'{year}-{month:02d}-15'
                d[complete_month] = idx.get(country, {}).get(
                    complete_month, 0
                )
        d_list.append(d)

    TSVFile(ALL_BY_MONTH_PATH).write(d_list)
    log.info(f'Saved {ALL_BY_MONTH_PATH}')


def by_region():
    d_list = TSVFile(ALL_BY_MONTH_PATH).read()
    idx = {}
    for d in d_list:
        country = d['country']
        # sub_region = find_sub_region(country)
        sub_region = country
        if sub_region not in idx:
            idx[sub_region] = {}

        for k, v in d.items():
            if k == 'country':
                continue
            value = String(v).int or 0
            idx[sub_region][k] = idx[sub_region].get(k, 0) + value
    d_list = []
    for sub_region, d in idx.items():
        total = sum(d.values())
        d = dict(sub_region=sub_region, total=total, **d)
        d_list.append(d)

    d_list = sorted(d_list, key=lambda d: d['total'], reverse=True)

    TSVFile(ALL_BY_REGION).write(d_list)
    log.info(f'Saved {ALL_BY_REGION}')


if __name__ == '__main__':
    # clean_data()
    # by_month()
    by_region()
