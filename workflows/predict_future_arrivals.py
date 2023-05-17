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
    t, y = parse_arrivals_data()
    tseries = TimeSeries(y, window=WINDOW)
    for j in range(12):
        i = len(y) - j - 1
        x_evaluate = y[i - WINDOW: i].reshape(1, WINDOW)
        y_evaluate = y[i]
        yhat_evaluate = tseries.evaluate(x_evaluate)
        print(
            i,
            y_evaluate,
            yhat_evaluate,
            TIME_FORMAT_DATE.stringify(Time(t[i])),
        )
