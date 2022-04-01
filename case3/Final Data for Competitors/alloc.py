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

#Figure out how to do test train splits w/o scipy

def calc_implied_expected_returns(lamb, var_covar_matrix, w_mkt):
  if w_mkt.ndim == 1:
    w_mkt = w_mkt[ : , np.newaxis]
  if var_covar_matrix.ndim == 1:
    var_covar_matrix = var_covar_matrix[ : , np.newaxis]
  print(var_covar_matrix)
  print(w_mkt)
  print(np.matmul(var_covar_matrix, w_mkt.T))
  return lamb * np.matmul(var_covar_matrix, w_mkt.T)

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

def calc_sigma(weights, var_covar_mat):
  #Note that this is the standard deviation, and can be calculated by w_portfolio Sigma w_portfolio.T
  #Where Sigma is the var/covar matrix
  if weights.ndim == 1:
    weights = weights[ : , np.newaxis]
  return (weights @ var_covar_mat) @ weights.T

def black_litterman(covar_matrix, analyst_covar_matrix, implied_expected_returns, analyst_return_predictions):
  print(covar_matrix.shape)
  print(analyst_covar_matrix.shape)
  print(implied_expected_returns.shape)
  print(analyst_return_predictions.shape)
  return np.matmul(np.linalg.inv(np.linalg.inv(covar_matrix) + np.linalg.inv(analyst_covar_matrix)), np.matmul(np.linalg.inv(covar_matrix), implied_expected_returns) + np.matmul(np.linalg.inv(covar_matrix), analyst_return_predictions))


# def sharpe(lamb, test_data, analyst1, analyst2, analyst3, t_i):
#   w_mkt = calc_w_mkt_matrix(test_data.iloc[t_i])
#   var_covar_matrix = calc_var_covar_matrix(test_data)
#   implied_expected_returns = calc_implicit_expected_returns(lamb, var_covar_matrix, w_mkt)
#   expected_returns = black_litterman(var_covar_matrix, implied_expected_returns, expected_return_predictions)
#   lil_sigma = 1

#   return -1 * expected_returns / lil_sigma #-1 because we want to maximize


# The actual function that they will be running. 

#allocate_portfolio() is going to be run 2520 times, one time for each of the 2520 timesteps
#Each timestep, we will be given the analyst predictions for 21 days ahead of the beginning of the current month (??), which takes the form of a 9-element array (1 element per stock)

#creating the empty training dataframes
test_data_train = pd.DataFrame(columns=["A", "B", "C", "D", "E", "F", "G", "H", "I"])
analyst1_train = pd.DataFrame(columns=["A", "B", "C", "D", "E", "F", "G", "H", "I"])
analyst2_train = pd.DataFrame(columns=["A", "B", "C", "D", "E", "F", "G", "H", "I"])
analyst3_train = pd.DataFrame(columns=["A", "B", "C", "D", "E", "F", "G", "H", "I"])
w = np.array([1/9]*9) #initialize as an even distribution of our portfolio

def allocate_portfolio(asset_prices, asset_price_predictions_1, asset_price_predictions_2, asset_price_predictions_3):
    #As per Piazza instructions, appending the new data into the existing dataframes
    # test_data_train.loc[len(test_data)] = asset_prices
    # analyst1_train.loc[len(analyst1)] = asset_price_predictions_1
    # analyst2_train.loc[len(analyst2)] = asset_price_predictions_2
    # analyst3_train.loc[len(analyst3)] = asset_price_predictions_3

    # lamb_0 = 1
    # market_caps = np.multiply(asset_prices, shares)
    # total_market_cap_in_portfolio = np.sum(market_caps)
    # w_mkt = np.multiply(market_caps, w) #for stocks A through I

    # analyst_return_predictions = asset_price_predictions_1 - analyst1_train.iloc[-1]
    # analyst_return_predictions = analyst_return_predictions[ :, np.newaxis]
    # analyst_covar_matrix  = np.var(analyst_return_predictions)
    # returns = asset_prices-test_data_train.iloc[-1]
    
    # print(returns)
    # returns = returns[ : , np.newaxis]
    # covar_matrix = np.cov(returns)
    # print(len(test_data_train))
    # if len(test_data_train) == 1:
    #   covar_matrix = calc_var_covar_matrix(test_data)
    #   print("first case!")
    # print(covar_matrix)
    # print(w_mkt)

    # print(covar_matrix.shape)
    # print(w_mkt.shape)
    # implied_expected_returns = calc_implied_expected_returns(lamb_0, covar_matrix, w_mkt)
    # expected_returns = black_litterman(covar_matrix, np.cov(analyst_return_predictions), implied_expected_returns, analyst_return_predictions)
    # variance = calc_sigma(w_mkt, covar_matrix)
    # variance = np.matmul(np.matmul(w_mkt.T, covar_matrix),w_mkt)


    #We want to maximize sharpe wrt lambda and weights
    # res = scipy.optimize.minimize(sharpe, lamb_0, method='nelder-mead', options={'xatol': 1e-8, 'disp': True})
    # This simple strategy equally weights all assets every period
    # (called a 1/n strategy).
    
    # n_assets = len(asset_prices)
    # weights = np.repeat(1 / n_assets, n_assets)

    # #L1 normalize the weights before returning
    # normalized_weights = weights/np.linalg.norm(weights, ord=1)
    # return normalized_weights

    # This simple strategy equally weights all assets every period
    # (called a 1/n strategy).
    
    n_assets = len(asset_prices)
    weights = np.repeat(1 / n_assets, n_assets)
    return weights


#Testing the runtime of the allocate_portfolio
returns = np.zeros(2520)
print(test_data.shape)
for i in range(1, 2508):
  #index from column 1 bc don't want row indices
  weights = allocate_portfolio(test_data.iloc[i], analyst1.iloc[i, 1:], analyst2.iloc[i, 1:], analyst3.iloc[i, 1:])
  # print(test_data.iloc[i]-test_data.iloc[i-1])
  # print((test_data[i]-test_data[i-1]) * weights)

  returns[i] = np.sum((test_data.iloc[i]-test_data.iloc[i-1]) * weights) #returns = sum((price_i - price_{i-1}) * weight stock k * number of shares of stock k)
  print(weights)

expected_returns = np.average(returns)
variance_returns = np.var(returns)
sharpe = expected_returns / variance_returns
print("sharpe: ")
print(sharpe)
