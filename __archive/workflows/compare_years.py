import os

import matplotlib.pyplot as plt

from workflows.predict_future_arrivals import get_month, get_proj_data


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

    png_file = os.path.join('charts', 'compare_years.png')
    plt.grid(True)
    plt.savefig(png_file)
    os.startfile(png_file)


if __name__ == '__main__':
    y, y_next, n_actual = get_proj_data()
    compare_years(y, y_next, n_actual)
