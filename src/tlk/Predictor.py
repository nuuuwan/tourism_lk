import numpy as np
from sklearn.linear_model import LinearRegression
from utils import Log

from tlk import Chart
from tlk.ArrivalsData import ArrivalsData

log = Log('Predictor')

M = 12 * 3  # training window in months


class Predictor:
    def get_prediction_data(self):
        data_list = ArrivalsData.from_file()
        log.debug(f'len(data_list)={len(data_list)}')

        log.debug(f'{M=}')
        y = [data.arrivals for data in data_list[M:]]
        n = len(y)
        log.debug(f'{n=}')

        x = []
        for i in range(n):
            xi = [data.arrivals for data in data_list[i: i + M]]
            x.append(xi)

        X = np.array(x)
        Y = np.array(y)

        log.debug(X.shape)
        log.debug(Y.shape)

        model = LinearRegression()
        model.fit(X, Y)
        Chart.Model((model.coef_, M)).save()

        yhat = []
        for i in range(n):
            xi = X[i]
            yhati = model.predict([xi])[0]
            if yhati < 0:
                yhati = 0
            yhat.append(yhati)

        plt_x = [data.date for data in data_list[M:]]

        # Future
        xi = np.array(xi[1:].tolist() + [y[-1]])
        x_2023 = ['01']
        y_2023 = [y[-1]]

        for i in range(11):
            yhati = model.predict([xi])[0]
            xi = np.array(xi[1:].tolist() + [yhati])
            month = i + 2
            date = f'{month:02d}'
            
            x_2023.append(date)
            y_2023.append(yhati)

        y_list = [y_2023]
        for i in range(1, 5):
            y_his = y[-12*i - 1: -12 *(i - 1) - 1]
            print(i, y_his)
            y_list.append(y_his)

        

        Chart.Predict2023(y_list, compare=False).save()
        
        Chart.Predict2023(y_list).save()
        Chart.Predict2023Cumulative(y_list).save()

        return (plt_x, y, yhat)


if __name__ == '__main__':
    log.debug('Before training...')
    prediction = Predictor()
    prediction_data = prediction.get_prediction_data()

    Chart.AllTimeActualAndPrediction(prediction_data).save()
    Chart.AllTimeError(prediction_data).save()

    Chart.LastDecadeActualAndPrediction(prediction_data).save()
    Chart.LastDecadeError(prediction_data).save()

    Chart.LastDecadeActualAndPrediction(prediction_data).save()
    Chart.LastDecadeError(prediction_data).save()

