import datetime
import os

import matplotlib.dates as mdates
from matplotlib import pyplot as plt

from ml import TimeSeries
from workflows.predict_future_arrivals import parse_arrivals_data


def verify(n_display=12):
    t, y = parse_arrivals_data()
    n_data = len(y)
    WINDOW = 12 * 3
    MIN_TRAINING_DATA = 20

    ys_actual = []
    ys_proj = []
    dis = []
    for i in range(MIN_TRAINING_DATA + WINDOW, n_data):
        t_series = TimeSeries(y[i - MIN_TRAINING_DATA - WINDOW: i], WINDOW)
        y_next_proj = max(0, t_series.project(n_steps=1)[0])
        y_next_actual = y[i]
        ti = t[i]
        di = datetime.datetime.fromtimestamp(ti)
        print(i, di, y_next_proj, y_next_actual)

        ys_actual.append(y_next_actual)
        ys_proj.append(y_next_proj)
        dis.append(di)

    ys_actual = ys_actual[-n_display:]
    ys_proj = ys_proj[-n_display:]
    dis = dis[-n_display:]

    fig, ax = plt.subplots()
    fig.set_size_inches(16, 9)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

    ax.plot(
        dis,
        ys_actual,
        label='actual',
        color='blue',
        linewidth=2,
    )
    ax.plot(
        dis,
        ys_proj,
        label='projection',
        color='blue',
        linewidth=2,
        linestyle="dotted",
    )

    ax.set_ylabel('Tourist Arrivals')
    ax.set_title(
        'Sri Lanka - Tourist Arrivals'
        + f' - Actual vs. Projection (Last {n_display} months)'
    )
    plt.legend(loc='lower right')

    png_file = os.path.join('charts', 'model_accuracy.png')
    plt.grid(True)
    plt.savefig(png_file)
    os.startfile(png_file)


if __name__ == '__main__':
    verify(24)
