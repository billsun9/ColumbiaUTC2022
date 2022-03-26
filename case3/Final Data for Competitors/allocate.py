import numpy as np
import pandas as pd
import scipy

#########################################################################
## Change this code to take in all asset price data and predictions    ##
## for one day and allocate your portfolio accordingly.                ##
#########################################################################
test_data = pd.read_csv("Acutal Testing Data.csv")
analyst1 = pd.read_csv("Predicted Testing Data Analyst 1.csv")
analyst2 = pd.read_csv("Predicted Testing Data Analyst 2.csv")
analyst3 = pd.read_csv("Predicted Testing Data Analyst 3.csv")

#Figure out how to do test train splits w/o scipy

def calc_implicit_expected_returns(lamb, var_covar_matrix, w_mkt):
  if var_covar_matrix.shape[1] != w_mkt.shape[0]:
    return "error"
  return lamb * np.matmul(var_covar_matrix, w_mkt)

def calc_var_covar_matrix(data):
  #calculating returns
  returns = data.pct_change()
  av = np.mean(returns, axis=0)
  return 0
def calc_sigma():
  return 0

def black_litterman(var_covar_matrix, implied_expected_returns, expected_return_predictions):
  return 0
def allocate_portfolio(asset_prices, asset_price_predictions_1, asset_price_predictions_2, asset_price_predictions_3):
    
    # This simple strategy equally weights all assets every period
    # (called a 1/n strategy).
    
    n_assets = len(asset_prices)
    weights = np.repeat(1 / n_assets, n_assets)
    return weights


#Running the code
w_mkt = allocate_portfolio(test_data, analyst1, analyst2, analyst3)
var_covar_matrix = calc_var_covar_matrix(test_data)
implied_expected_returns = calc_implicit_expected_returns(lamb, var_covar_matrix, w_mkt)
expected_returns = black_litterman(var_covar_matrix, implied_expected_returns, expected_return_predictions)
lil_sigma = 1

def sharpe(lamb, test_data, analyst1, analyst2, analyst3):
  w_mkt = allocate_portfolio(test_data, analyst1, analyst2, analyst3)
  var_covar_matrix = calc_var_covar_matrix(test_data)
  implied_expected_returns = calc_implicit_expected_returns(lamb, var_covar_matrix, w_mkt)
  expected_returns = black_litterman(var_covar_matrix, implied_expected_returns, expected_return_predictions)
  lil_sigma = 1

  return -1 * expected_returns / lil_sigma #-1 because we want to maximize

#We want to maximize sharpe wrt lambda and weights

#initialization
lamb_0 = 0.5
w_mkt = np.array(9) #for stocks A through I

res = scipy.optimize.minimize(sharpe, lamb_0, method='nelder-mead', options={'xatol': 1e-8, 'disp': True})
print(res.x) #printing the parameters that maximize Sharpe ratio
print(res)

print(test_data.head())
