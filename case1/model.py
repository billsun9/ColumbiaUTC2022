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
prices = pd.read_csv(DATA_PATH+'prices_2016.csv')
rain = pd.read_csv(DATA_PATH+'rain_2016.csv')

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
# high rain => harder for loggers => higher spot prices
