from functools import cached_property

import numpy as np
from sklearn.linear_model import LinearRegression
from tlk.ArrivalsData import ArrivalsData
from utils import Log

from tlk import Chart

log = Log('Predictor')

M = 12 * 3  # training window in months


class Predictor:
    @cached_property
    def data_list(self):
        return ArrivalsData.from_file()

    @cached_property
    def training_data(self):
        data_list = self.data_list
        y = [data.arrivals for data in data_list[M:]]
        n = len(y)
        x = []
        for i in range(n):
            xi = [data.arrivals for data in data_list[i: i + M]]
            x.append(xi)

        x = np.array(x)
        y = np.array(y)
        return [x, y]

    @cached_property
    def model(self):
        x, y = self.training_data
        model = LinearRegression()
        model.fit(x, y)
        return model

    @cached_property
    def prediction(self):
        model = self.model
        x, y = self.training_data
        n = len(y)
        yhat = []
        for i in range(n):
            yhati = model.predict([x[i]])[0]
            if yhati < 0:
                yhati = 0
            yhat.append(yhati)
        return yhat

    @property
    def plt_x(self):
        return [data.date for data in self.data_list[M:]]

    def get_future_projection(self, hardcoded_next_month=None):
        [x, y] = self.training_data
        model = self.model

        xi = np.array(x[-1][1:].tolist() + [y[-1]])
        plt_x_projection = ['01']
        y_projection = [y[-1]]

        for i in range(11):
            yhati = max(0, model.predict([xi])[0])
            if i == 0 and hardcoded_next_month:
                yhati = hardcoded_next_month

            xi = np.array(xi[1:].tolist() + [yhati])
            month = i + 2
            date = f'{month:02d}'
            plt_x_projection.append(date)
            y_projection.append(yhati)

        return y_projection

    def get_future_projection_and_history(self):
        [x, y] = self.training_data
        y2023 = self.get_future_projection()
        print('2023', y2023)
        ylist_by_year = [y2023]
        for i_year in range(0, 5):
            i_start = -12 * (i_year + 1) - 1
            i_end = i_start + 12
            yi_year = y[i_start:i_end]
            print(2022 - i_year, yi_year)
            ylist_by_year.append(yi_year)
        return ylist_by_year

    def get_future_prediction_with_hardcoded_next_months(
        self, hardcoded_next_month_list
    ):
        ylist_by_scenario = []
        for hardcoded_next_month in hardcoded_next_month_list:
            yscenario = predictor.get_future_projection(hardcoded_next_month)
            ylist_by_scenario.append(yscenario)
        return ylist_by_scenario


if __name__ == '__main__':
    predictor = Predictor()
    # hardcoded_next_month_list = [120_000, 187_000, 255_000]
    # ylist_by_scenario = (
    #     predictor.get_future_prediction_with_hardcoded_next_months(
    #         hardcoded_next_month_list
    #     )
    # )
    # Chart.Predict2023Hardcoded(ylist_by_scenario).save()

    [x, y] = predictor.training_data

    model = predictor.model
    Chart.Model((model.coef_, M)).save()

    # plt_x = predictor.plt_x
    # yhat = predictor.prediction

    # # Actual and Prediction
    # Chart.AllTimeActualAndPrediction((plt_x, y, yhat)).save()
    # Chart.LastDecadeActualAndPrediction((plt_x, y, yhat)).save()

    # # Errors
    # Chart.AllTimeError((plt_x, y, yhat)).save()
    # Chart.LastDecadeError((plt_x, y, yhat)).save()

    # Future
    ylist_by_year = predictor.get_future_projection_and_history()
    Chart.Predict2023((ylist_by_year), compare=False).save()
    # Chart.Predict2023((ylist_by_year), compare=True).save()

    Chart.Predict2023Cumulative((ylist_by_year), compare=False).save()
    Chart.Predict2023Cumulative((ylist_by_year), compare=True).save()
