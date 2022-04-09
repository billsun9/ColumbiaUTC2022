# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 11:12:42 2022

@author: Bill Sun
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
import xgboost

DATA_PATH = 'Case 1 Training Data/'
# %%
prices = pd.read_csv(DATA_PATH+'prices_2018.csv')
rain = pd.read_csv(DATA_PATH+'rain_2018.csv')

# %%
# daily prices
r = []
for rain_per_m in rain['Historical Monthly Rain']: r.extend([rain_per_m] * 21)
plt.plot(list(range(252)), prices['Daily Price'], label="daily prices")
plt.plot(list(range(252)), r, label="rain")
plt.legend()
plt.show()
# %%
# monthly price averages
r = []
for rain_per_m in rain['Historical Monthly Rain']: r.extend([rain_per_m] * 21)
p = []
for i in range(12):
    avg = prices['Daily Price'][21*i: 21*(i+1)].mean()
    p.extend([avg] * 21)
plt.plot(list(range(252)), p, label="avg monthly prices")
plt.plot(list(range(252)), r, label="rain")
plt.legend()
plt.show()
# %%
X = rain.to_numpy()[:,1].reshape(-1,1)
X = np.append(X, np.array(list(range(1,13))).reshape(-1,1), axis=1)
Y = prices.to_numpy()[:,1].reshape(12,21)
# %%
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
# high rain => harder for loggers => higher spot prices
model = LinearRegression()
model.fit(X, Y)
# %%
pred = model.predict(X[11].reshape(1,-1))
print("mse: %s" % str(mean_squared_error(Y[11].reshape(1,-1), pred)))