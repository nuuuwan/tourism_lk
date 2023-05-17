import os

import numpy as np
from utils import TIME_FORMAT_DATE, Time, TSVFile

from ml import TimeSeries


def parse_arrivals_data():
    d_list = TSVFile(
        os.path.join('data/sri_lanka.tourism.arrivals.by_month.tsv')
    ).read()
    t = [TIME_FORMAT_DATE.parse(d['month']).ut for d in d_list]
    y = [int(d['arrivals']) for d in d_list]
    return np.array(t), np.array(y)


if __name__ == '__main__':
    WINDOW = 12 * 3
    STEPS = 7
    t, y = parse_arrivals_data()
    tseries = TimeSeries(y, window=WINDOW)
    y_next = tseries.project(n_steps=STEPS)

    for i in range(STEPS):
        ti = t[-1] + (i + 1) * 24 * 60 * 60 * 30
        print(i, ti)
        print(f'{TIME_FORMAT_DATE.stringify(Time(ti))}: {y_next[i]}')
