import numpy as np
import pandas as pd
import scipy

#########################################################################
## Change this code to take in all asset price data and predictions    ##
## for one day and allocate your portfolio accordingly.                ##
#########################################################################
test_data = pd.read_csv("Acutal Testing Data.csv")
test_data = test_data.iloc[:, 1:]

analyst1 = pd.read_csv("Predicted Testing Data Analyst 1.csv")
analyst2 = pd.read_csv("Predicted Testing Data Analyst 2.csv")
analyst3 = pd.read_csv("Predicted Testing Data Analyst 3.csv")
shares = pd.read_csv("Shares Outstanding.csv")
shares = shares.iloc[:, 1:]
# %%
returns = pd.DataFrame()

for col in test_data.columns:
    returns[col] = test_data[col].pct_change().apply(lambda x: np.log(1+x))
# %%
# cov
cov_matrix = returns.cov() * 252
# %%
# port var
weights=np.array([1/9,1/9,1/9,1/9,1/9,1/9,1/9,1/9,1/9])
port_var = np.dot(weights.T, np.dot(cov_matrix,weights))
# %%
# annual portfolio return
simpleAnnualReturn = np.sum(returns.mean()*weights)*252