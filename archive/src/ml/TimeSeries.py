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

    def eval(self, x_eval: np.array):
        assert x_eval.shape == (
            1,
            self.window,
        ), f'{x_eval.shape} != {(self.window,)}'
        model = self.model
        yhat = model.predict(x_eval)[0]
        return yhat

    def project(self, n_steps: int):
        n_data = len(self.y)
        y_copy = np.array(self.y)
        for i in range(n_steps):
            x_eval = y_copy[-self.window:].reshape(1, self.window)
            yhat = self.eval(x_eval)
            y_copy = np.append(y_copy, yhat)
            assert y_copy.shape == (
                n_data + i + 1,
            ), f'{y_copy.shape} != {(n_data + i + 1,)}'
        y_next = y_copy[-n_steps:]
        assert y_next.shape == (n_steps,), f'{y_next.shape} != {(n_steps,)}'
        return y_next
