import numpy as np
from sklearn.linear_model import LinearRegression
from utils import Log
import matplotlib.pyplot as plt
from tlk.ArrivalsData import ArrivalsData
import math
log = Log('Predictor')


m = 36

def error_func(z, zhat):
    MAX_ABS = 10
    if zhat == 0:
        return MAX_ABS
    if z == 0:
        return 1/MAX_ABS
    r = z / zhat    
    
    return max(min(r, MAX_ABS), 1/MAX_ABS)

def filter_last_decade(prediction_data):
    (plt_x, y, yhat) = prediction_data
    i_min = -12 * 10 - 1
    plt_x = plt_x[i_min:]
    y = y[i_min:]
    yhat = yhat[i_min:]
    return (plt_x, y, yhat)

def get_error(y, yhat):
    return [error_func(y[i],yhat[i]) for i in range(len(y))]

class Predictor:
    def get_prediction_data(self):
        data_list = ArrivalsData.from_file()
        log.debug(f'len(data_list)={len(data_list)}')
        
        log.debug(f'{m=}')
        y = [data.arrivals for data in data_list[m:]]
        n = len(y)
        log.debug(f'{n=}')

        x = []
        for i in range(n):
            xi = [data.arrivals for data in data_list[i: i + m]]
            x.append(xi)

        X = np.array(x)
        Y = np.array(y)
    
        log.debug(X.shape)
        log.debug(Y.shape)

        model = LinearRegression()
        model.fit(X, Y)
        self.plot_model(model.coef_)
        

        yhat = []
        for i in range(n):
            xi = X[i]
            yhati = model.predict([xi])[0]
            if yhati < 0:
                yhati = 0
            yhat.append(yhati)

        plt_x = [data.date for data in data_list[m:]]

        # Future
        print(xi)
        print(xi[1:])
        
        xi = np.array(xi[1:].tolist() + [y[-1]] )

        x_2023 = ['01']
        y_2023 = [y[-1]]

        for i in range(11):
            yhati = model.predict([xi])[0]
            xi = np.array(xi[1:].tolist() + [yhati])
            month = i + 2
            date = f'{month:02d}'
            print(f'{date}\t{yhati}')

            x_2023.append(date)
            y_2023.append(yhati)

        y_2022 = y[-12-1:-12*0-1]
        y_2019 = y[-12*4-1:-12*3-1]
        y_2018= y[-12*5-1:-12*4-1]

        self.plot_2023(y_2023, y_2022, y_2019, y_2018)
        

        return (plt_x, y, yhat)

    def plot_2023(self, y_2023, y_2022, y_2019, y_2018):
        x = [f'{month:02d}' for month in range(1,12+1)]
        plt.figure(figsize=(24, 8))                  
        plt.plot(x, y_2023, 'g', label='Prediction (2023)')        
        plt.plot(x, y_2022, 'b', label='2022')   
        plt.plot(x, y_2019, 'red', label='2019')   
        plt.plot(x, y_2018, 'orange', label='2018')   
        
        plt.xticks([f'{month:02d}' for month in range(1,12+1)])    
        plt.title('Prediction (2023)') 
        plt.legend()
        
        png_file_path='charts/arrivals_predicted.2023.png'
        plt.savefig(png_file_path)
        log.info(f'Saved chart to {png_file_path}')
        plt.close()
        

    def plot_all(self, prediction_data):
        (plt_x, y, yhat) = prediction_data
        plt.figure(figsize=(24, 8))                  
        plt.plot(plt_x, y, 'b', label='Actual')
        plt.plot(plt_x, yhat, 'g', label='Prediction')        
        
        plt.xticks([f'{year}-01' for year in range(1975, 2025,5)])  
        plt.title('Prediction [Green] vs. Actual [Blue] (1972 - present)') 
        plt.legend()
        
        png_file_path='charts/arrivals_predicted.all.png'
        plt.savefig(png_file_path)
        log.info(f'Saved chart to {png_file_path}')
        plt.close()

        
    def plot_2022(self, prediction_data):
        (plt_x, y, yhat) = filter_last_decade(prediction_data)
                   
        plt.figure(figsize=(24, 8))                  
        plt.plot(plt_x, y, 'b', label='Actual')
        plt.plot(plt_x, yhat, 'g', label='Prediction')        
        
        plt.xticks([f'{year}-01' for year in range(2013,2024)])    
        plt.title('Prediction [Green] vs. Actual [Blue] (2013 - present)') 
        plt.legend()
        
        png_file_path='charts/arrivals_predicted.2022.png'
        plt.savefig(png_file_path)
        log.info(f'Saved chart to {png_file_path}')
        plt.close()

    def plot_error_all(self, prediction_data):
        (plt_x, y, yhat) = prediction_data
        error = get_error(y, yhat)
            
        plt.figure(figsize=(24, 8))                  
        plt.plot(plt_x, error, 'r')                
        plt.xticks([f'{year}-01' for year in range(1975, 2025,5)]) 
        plt.gca().set_yscale('log',base=2)
        plt.yticks([2 ** x for x in range(-3,4)])
        plt.title('Prediction Error (1972 - present)') 

        for i in range(len(plt_x)):
            if error[i] < 0.7:
                print(f'{plt_x[i]}: {error[i]}')
        
        
        png_file_path='charts/arrivals_predicted.error.all.png'
        
        plt.savefig(png_file_path)
        log.info(f'Saved chart to {png_file_path}')
        plt.close()

    def plot_error_2022(self, prediction_data):
        (plt_x, y, yhat) = filter_last_decade(prediction_data)
        
        error = get_error(y, yhat)
            
        plt.figure(figsize=(24, 8))                  
        plt.plot(plt_x, error, 'r')
        
        plt.xticks([f'{year}-01' for year in range(2013,2024)])  
        plt.gca().set_yscale('log',base=2)
        plt.yticks([2 ** x for x in range(-3,4)])
        plt.title('Prediction Error (2013 - present)')
        
        png_file_path='charts/arrivals_predicted.error.2022.png'
        
        plt.savefig(png_file_path)
        log.info(f'Saved chart to {png_file_path}')
        plt.close()  

    def plot_model(self, coefs):
        x = [m - i for i in range(m)]
        y = coefs
        plt.bar(x, y)

        plt.title('Model Feature Weights')
        
        png_file_path='charts/arrivals_predicted.model.png'
        
        plt.savefig(png_file_path)
        log.info(f'Saved chart to {png_file_path}')
        plt.close()  

        
          


if __name__ == '__main__':
    log.debug('Before training...')
    prediction =  Predictor()
    prediction_data = prediction.get_prediction_data()
    prediction.plot_all(prediction_data)
    prediction.plot_2022(prediction_data)
    prediction.plot_error_all(prediction_data)
    prediction.plot_error_2022(prediction_data)
