import os

import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from matplotlib import rcParams
from utils import Log

log = Log('Predictor')

DEFAULT_FIGSIZE = (8, 4.5)

ANNOTATIONS = {
    '1983-08': 'Black July (1983)',
    '2001-08': 'BIA Attacks (2001)',
    '2019-05': 'Easter Attacks (2019)',
    '2020-03': 'CoViD-19 Pandemic (2020)',
}

rcParams['font.family'] = 'PT Sans'


LEGEND_LOC = 'upper left'


class GenericChart:
    def __init__(self, data):
        self.data = data

    @property
    def title(self):
        return self.__class__.__name__

    @property
    def xlabel(self):
        return 'Month (End)'

    @property
    def ylabel(self):
        return 'Y'

    @property
    def filtered_data(self):
        return self.data

    @property
    def xticks(self):
        return []

    def draw(self):
        pass

    @staticmethod
    def annotate(x, y):
        n = len(x)
        for i in range(n):
            xi = x[i]
            yi = y[i]

            for xi_a, label in ANNOTATIONS.items():
                if xi == xi_a:
                    plt.gca().annotate(
                        label,
                        xy=(i, yi),
                        xycoords='data',
                        xytext=(i, yi),
                        color="#f80",
                        textcoords='data',
                        horizontalalignment='center',
                        verticalalignment='top',
                    )

    @property
    def png_file_path(self):
        return os.path.join('charts', self.__class__.__name__ + '.png')

    def save(self):
        plt.figure(figsize=DEFAULT_FIGSIZE)
        self.draw()

        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend(loc=LEGEND_LOC)
        plt.xticks(self.xticks)

        plt.grid(b=True, which='major', color='#888')
        plt.grid(b=True, which='minor', color='#eee')
        plt.minorticks_on()

        png_file_path = self.png_file_path
        plt.savefig(png_file_path)
        plt.close()
        os.system(f'open -a firefox "{png_file_path}"')
        log.info(f'Saved chart to {png_file_path}')


class AllTime(GenericChart):
    @property
    def title(self):
        return 'Tourist Arrivals (Monthly - 1975 to present)'

    @property
    def xticks(self):
        return [f'{year}-01' for year in range(1975, 2025, 5)]


class LastDecade(GenericChart):
    @property
    def title(self):
        return 'Tourist Arrivals (Monthly - 2013 to present)'

    @property
    def filtered_data(self):
        (plt_x, y, yhat) = self.data
        i_min = -12 * 10 - 1
        filtered_plt_x = plt_x[i_min:]
        filtered_y = y[i_min:]
        filtered_yhat = yhat[i_min:]
        return (filtered_plt_x, filtered_y, filtered_yhat)

    @property
    def xticks(self):
        return [f'{year}-01' for year in range(2013, 2024)]


class ActualAndPrediction(GenericChart):
    @property
    def title(self):
        return 'Actual & Predicted'

    @property
    def ylabel(self):
        return 'Tourist Arrivals'

    def draw(self):
        (plt_x, y, yhat) = self.filtered_data

        plt.gca().get_yaxis().set_major_formatter(
            tk.FuncFormatter(lambda x, p: f'{x / 1000.0 : .0f}K'),
        )

        plt.plot(plt_x, y, 'b', label='Actual')
        plt.plot(plt_x, yhat, 'g', label='Prediction')
        GenericChart.annotate(plt_x, y)


class Error(GenericChart):
    BASE = 2
    MAX_EXP = 3

    @property
    def title(self):
        return 'Model Error Ratio (Actual / Predicted)'

    @property
    def ylabel(self):
        return 'Model Error Ratio (Actual / Predicted)'

    @staticmethod
    def error_func(z, zhat):
        MAX_ABS = Error.BASE**Error.MAX_EXP
        if zhat == 0:
            return MAX_ABS
        if z == 0:
            return 1 / MAX_ABS
        r = z / zhat

        return max(min(r, MAX_ABS), 1 / MAX_ABS)

    def draw(self):
        (plt_x, y, yhat) = self.filtered_data
        error = [Error.error_func(yi, yhati) for yi, yhati in zip(y, yhat)]
        plt.plot(plt_x, error, 'r', label='Model Error Ratio')
        GenericChart.annotate(plt_x, error)

        plt.yscale('log', base=Error.BASE)
        plt.yticks(
            [
                Error.BASE**i
                for i in range(-Error.MAX_EXP, Error.MAX_EXP + 1)
            ]
        )


class AllTimeActualAndPrediction(AllTime, ActualAndPrediction):
    pass


class AllTimeError(AllTime, Error):
    pass


class LastDecadeActualAndPrediction(LastDecade, ActualAndPrediction):
    pass


class LastDecadeError(LastDecade, Error):
    pass


class Model(GenericChart):
    @property
    def title(self):
        return 'Model Weights'

    @property
    def xlabel(self):
        return 'Months Ago'

    @property
    def ylabel(self):
        return 'Model Weight'

    @property
    def xticks(self):
        (_, M) = self.data
        return [M - i for i in range(M)]

    def draw(self):
        (coefs, _) = self.data
        x = self.xticks
        y = coefs
        plt.bar(x, y)


class Predict2023(GenericChart):
    @property
    def png_file_path(self):
        return os.path.join(
            'charts',
            self.__class__.__name__ + '.' + str(self.compare) + '.png',
        )

    def __init__(self, data, compare=True):
        GenericChart.__init__(self, data)
        self.compare = compare

    @property
    def title(self):
        return 'Predicted Tourists Arrivals in 2023'

    @property
    def xticks(self):
        return [f'{month:02d}' for month in range(1, 12 + 1)]

    @property
    def ylabel(self):
        return 'Predicted Tourist Arrivals'

    def draw(self):
        x = self.xticks
        y_list = self.filtered_data

        plt.gca().get_yaxis().set_major_formatter(
            tk.FuncFormatter(lambda x, p: f'{x / 1000.0 : .0f}K'),
        )

        plt.plot(x, y_list[0], 'g', label='2023 (Prediction)')

        if self.compare:
            colors = ['blue', 'orange', 'red', 'brown', 'black']
            for i in range(len(y_list) - 1):
                plt.plot(x, y_list[i + 1], colors[i], label=str(2023 - i - 1))

            plt.gca().get_yaxis().set_major_formatter(
                tk.FuncFormatter(lambda x, p: f'{x / 1000.0 : .0f}K'),
            )


class Predict2023Cumulative(Predict2023):
    @property
    def title(self):
        return 'Predicted Cumulative Tourists Arrivals in 2023'

    @property
    def ylabel(self):
        return 'Predicted Cumulative Tourist Arrivals'

    @property
    def filtered_data(self):
        y_list = self.data
        cum_list = []
        for y in y_list:
            cum = []
            cum_yi = 0
            for yi in y:
                cum_yi += yi
                cum.append(cum_yi)
            cum_list.append(cum)
        return cum_list


class Predict2023Hardcoded(GenericChart):
    @property
    def png_file_path(self):
        return os.path.join(
            'charts',
            self.__class__.__name__ + '.' + '.png',
        )

    def __init__(self, data, compare=True):
        GenericChart.__init__(self, data)
        self.compare = compare

    @property
    def title(self):
        return 'Predicted Tourists Arrivals in 2023'

    @property
    def xticks(self):
        return [f'{month:02d}' for month in range(1, 12 + 1)]

    @property
    def ylabel(self):
        return 'Predicted Tourist Arrivals'

    def draw(self):
        x = self.xticks
        y_list = self.filtered_data

        plt.gca().get_yaxis().set_major_formatter(
            tk.FuncFormatter(lambda x, p: f'{x / 1000.0 : .0f}K'),
        )

        colors = ['red', 'orange', 'green']
        labels = ['1M', '1.5M', '2M']
        for i in range(len(y_list)):
            plt.plot(x, y_list[i], colors[i], label=labels[i])

        plt.gca().get_yaxis().set_major_formatter(
            tk.FuncFormatter(lambda x, p: f'{x / 1000.0 : .0f}K'),
        )
