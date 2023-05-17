from functools import cached_property

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.linear_model import LinearRegression


class TimeSeries:
    def __init__(self, y: np.array, window: int):
        self.y = y
        self.window = window

    @cached_property
    def train_data(self):
        n_data = len(self.y)
        n_train = n_data - self.window

        x_train = sliding_window_view(self.y[:-1], self.window)
        assert x_train.shape == (
            n_train,
            self.window,
        ), f'{x_train.shape} != {(n_train, self.window)}'

        y_train = self.y[self.window:]
        assert y_train.shape == (n_train,), f'{y_train.shape} != {(n_train)}'

        return x_train, y_train

    @cached_property
    def model(self):
        x, y = self.train_data
        model = LinearRegression()
        model.fit(x, y)
        return model

    def evaluate(self, x_evaluate: np.array):
        assert x_evaluate.shape == (
            1,
            self.window,
        ), f'{x_evaluate.shape} != {(self.window,)}'
        model = self.model
        yhat = model.predict(x_evaluate)
        return yhat
