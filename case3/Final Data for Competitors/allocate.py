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
print(analyst1.head())
#Figure out how to do test train splits w/o scipy

def calc_implied_expected_returns(lamb, var_covar_matrix, w_mkt):
  # if var_covar_matrix.shape[1] != w_mkt.shape[0]:
  #   return "error"
  return lamb * np.matmul(var_covar_matrix, w_mkt)

def calc_var_covar_matrix(data):
  #calculating returns
  returns = data.pct_change()
  returns = returns[1:]
  av = np.mean(returns, axis=0)
  excess_returns = returns-av
  #return excess_returns.cov() #is this the right way to calc covar or below?
  cov_matrix = 1/returns.shape[0] * excess_returns.T @ excess_returns
  return cov_matrix

def calc_w_mkt_matrix(price_vector):
  total_mkt_cap = np.dot(shares, price_vector)
  return price_vector / total_mkt_cap

def calc_analyst_covar(data):
  #calculating returns
  returns = data.pct_change()
  returns = returns.iloc[1:, 1:]
  return returns.cov()

print(calc_analyst_covar(analyst1))

def calc_sigma():
  return 0

def black_litterman(var_covar_matrix, analyst_covar_matrix, implied_expected_returns, expected_return_predictions):
  return np.matmul(np.linalg.pinv(np.linalg.pinv(var_covar_matrix) + np.linalg.pinv(analyst_covar_matrix)), np.matmul(np.linalg.pinv(var_covar_matrix), implied_expected_returns) + np.matmul(np.linalg.inv(var_covar_matrix), expected_return_predictions))

def allocate_portfolio(asset_prices, asset_price_predictions_1, asset_price_predictions_2, asset_price_predictions_3):
    
    # This simple strategy equally weights all assets every period
    # (called a 1/n strategy).
    
    n_assets = len(asset_prices)
    weights = np.repeat(1 / n_assets, n_assets)
    return weights

def sharpe(lamb, test_data, analyst1, analyst2, analyst3, t_i):
  w_mkt = calc_w_mkt_matrix(test_data.iloc[t_i])
  var_covar_matrix = calc_var_covar_matrix(test_data)
  implied_expected_returns = calc_implicit_expected_returns(lamb, var_covar_matrix, w_mkt)
  expected_returns = black_litterman(var_covar_matrix, implied_expected_returns, expected_return_predictions)
  lil_sigma = 1

  return -1 * expected_returns / lil_sigma #-1 because we want to maximize



# #Running the code
# #initialization
# lamb_0 = 1
# w_mkt = np.array(9) #for stocks A through I
# # w_mkt = allocate_portfolio(test_data, analyst1, analyst2, analyst3)
# var_covar_matrix = calc_var_covar_matrix(test_data)
# implied_expected_returns = calc_implicit_expected_returns(lamb_0, var_covar_matrix, w_mkt)
# expected_returns = black_litterman(var_covar_matrix, implied_expected_returns, expected_return_predictions)
# lil_sigma = 1


# #We want to maximize sharpe wrt lambda and weights



# res = scipy.optimize.minimize(sharpe, lamb_0, method='nelder-mead', options={'xatol': 1e-8, 'disp': True})
# print(res.x) #printing the parameters that maximize Sharpe ratio
# print(res)

# print(test_data.head())
