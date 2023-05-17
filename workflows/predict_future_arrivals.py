import calendar
import os

import matplotlib.pyplot as plt
import numpy as np
from utils import TIME_FORMAT_DATE, Time, TimeFormat, TSVFile

from ml import TimeSeries


def format_number(x: int):
    if x > 1_000_000:
        return f'~{x/1_000_000:.2f}M'

    if x > 1_000:
        return f'~{x/1_000:.0f}K'

    return f'{x}'


def get_month(i: int):
    return calendar.month_abbr[i + 1]


def parse_arrivals_data():
    d_list = TSVFile(
        os.path.join('data/sri_lanka.tourism.arrivals.by_month.tsv')
    ).read()
    t = [TIME_FORMAT_DATE.parse(d['month']).ut for d in d_list]
    y = [int(d['arrivals']) for d in d_list]
    return np.array(t), np.array(y)


def get_proj_data():
    WINDOW = 12 * 3
    t, y = parse_arrivals_data()
    n_actual = int(TimeFormat('%m').stringify(Time(t[-1])))
    n_steps = 12 - n_actual
    tseries = TimeSeries(y, window=WINDOW)
    y_next = tseries.project(n_steps=n_steps)
    return y, y_next, n_actual


def build_monthly_chart(y, y_next, n_actual):
    y_actual = y[-n_actual:].tolist()
    y_with_proj = y_actual + y_next.tolist()
    t_with_proj = [get_month(i) for i in range(12)]

    fig, ax = plt.subplots()
    fig.set_size_inches(8, 4.5)

    ax.bar(t_with_proj, y_with_proj, color="lightblue", label="projection")
    ax.bar(t_with_proj[:n_actual], y_actual, color="blue", label="actual")

    ax.set_ylabel('Tourist Arrivals')
    ax.set_title('Sri Lanka - Tourist Arrivals in 2023')
    ax.legend()

    png_file = os.path.join('charts', 'predict_future_arrivals.png')
    plt.grid(True)
    plt.savefig(png_file)
    os.startfile(png_file)

    total_for_year = format_number(sum(y_with_proj))
    end_actual = t_with_proj[n_actual - 1]
    cum_arrivals = format_number(sum(y_actual))
    next_arrivals = format_number(y_next[0])
    next_month = t_with_proj[n_actual]
    print(
        f'''
As of the end of {end_actual} 2023,
#SriLanka has seen {cum_arrivals} #tourist arrivals.

Our model predicts {next_arrivals} arrivals in {next_month} 2023,
and {total_for_year} total arrivals in 2023.

data: https://www.sltda.gov.lk/en/statistics (@sltda_srilanka)
    '''
    )


def compare_years(y, y_next, n_actual):
    n_data = len(y)
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 4.5)

    t = [get_month(i) for i in range(12)]

    y_actual = y[-n_actual:].tolist()
    y_current = y_actual + y_next.tolist()
    ax.plot(
        t,
        y_current,
        label=f'{2023}-projection',
        color='blue',
        linestyle="dotted",
        linewidth=2,
    )
    y_current = y[-n_actual:].tolist() + y_next.tolist()
    ax.plot(
        t[:n_actual],
        y_actual,
        label=f'{2023}-actual',
        color='blue',
        linewidth=2,
    )

    n_previous_years = 5
    colors = ['cyan', 'green', 'orange', 'red', 'black']
    for i in range(0, n_previous_years):
        i_start = n_data - n_actual - 12 * (i + 1)
        y_year = y[i_start: i_start + 12]
        ax.plot(
            t, y_year, label=f'{2023 - i-1}', color=colors[i], linewidth=2
        )

    ax.set_ylabel('Tourist Arrivals')
    first_year = 2023 - n_previous_years
    ax.set_title(f'Sri Lanka - Tourist Arrivals ({first_year} - present)')
    plt.legend(loc='upper right')

    png_file = os.path.join(
        'charts', 'predict_future_arrivals.compare_years.png'
    )
    plt.grid(True)
    plt.savefig(png_file)
    os.startfile(png_file)


if __name__ == '__main__':
    y, y_next, n_actual = get_proj_data()
    # build_monthly_chart(y, y_next, n_actual)
    compare_years(y, y_next, n_actual)
