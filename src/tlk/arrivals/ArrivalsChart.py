import matplotlib.pyplot as plt
from tlk.ArrivalsData import ArrivalsData
from utils import Log, TimeFormat

log = Log('ArrivalsChart')


class ArrivalsChart:
    def save(self):
        png_file_name = 'charts/sri_lanka.tourism.arrivals.by_month.png'
        data_list = ArrivalsData.from_file()
        x = [TimeFormat('%Y-%m').stringify(data.t) for data in data_list]
        y = [data.arrivals for data in data_list]
        plt.plot(x, y)

        plt.xticks(['1980-01', '2000-01', '2020-01'])

        plt.savefig(png_file_name)
        plt.close()
        log.info(f"Saved {png_file_name}")


if __name__ == '__main__':
    ArrivalsChart().save()
