import os

import matplotlib.pyplot as plt

from workflows.predict_future_arrivals import format_number, get_proj_data


def summary_by_year(y, y_next, n_actual):
    n_data = len(y)
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 4.5)

    n_years = int(n_data / 12)
    ys_year = []
    years = []
    year = 1972
    for i_year in range(0, n_years):
        y_year = sum(y[i_year * 12: (i_year + 1) * 12])
        ys_year.append(y_year)
        years.append(year)

        print(year, format_number(y_year))

        year += 1

    ax.bar(
        years,
        ys_year,
    )

    ax.set_ylabel('Annual Tourist Arrivals')
    ax.set_title('Sri Lanka - Tourist Arrivals (by year)')

    ax.set_yticklabels(
        [f'{value / 1_000_000:.1f}M' for value in ax.get_yticks()]
    )
    ax.annotate(
        text='2019',
        xy=(2019, 1913702),
        xycoords='data',
        xytext=(2023, 2333796),
        textcoords='data',
        fontsize='x-large',
        ha='center',
        va='center',
        color='r',
        arrowprops=dict(fc='r', ec='k'),
    )
    png_file = os.path.join('charts', 'summary_by_year.png')
    plt.grid(True)
    plt.savefig(png_file)
    os.startfile(png_file)


if __name__ == '__main__':
    y, y_next, n_actual = get_proj_data()
    summary_by_year(y, y_next, n_actual)
