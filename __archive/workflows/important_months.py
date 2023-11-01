import os

from utils import TimeFormat, TSVFile


def main():
    d_list = TSVFile(
        os.path.join('data', 'sri_lanka.tourism.arrivals.by_month.tsv')
    ).read()

    month_to_n = {}
    max_arrivals = 0
    for d in d_list:
        month, arrivals = d['month'], int(d['arrivals'])
        if arrivals >= max_arrivals:
            t = TimeFormat('%Y-%m-%d').parse(month)
            month_str = TimeFormat('%b %Y').stringify(t)

            print(f'{month_str} {arrivals/1000.0:,.0f}K')
            max_arrivals = arrivals

            month = month_str[:3]
            if month not in month_to_n:
                month_to_n[month] = 0
            month_to_n[month] += 1
    print(month_to_n)


if __name__ == '__main__':
    main()
