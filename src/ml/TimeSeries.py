from functools import cached_property
from sklearn.linear_model import LinearRegression
import numpy as np
class TimeSeries:
    def __init__(self, y: np.array, window: int):
        self.y = y
        self.window = window

    @cached_property
    def train_data(self):
        n_data = len(self.y)
        n_train = n_data - self.window
        x_train = []
        y_train = self.y[self.window:]
        for i in range(n_train):
            x_train.append(self.y[i:i+self.window])
        return np.array(x_train), np.array(y_train)


    @cached_property 
    def model(self):
        x, y = self.train_data
        model = LinearRegression()
        model.fit(x, y)
        return model

    def evaluate(self, x_evaluate: np.array):
        assert len(x_evaluate) == self.window
        model = self.model
        yhat = model.predict(x_evaluate)
        return yhat    



    