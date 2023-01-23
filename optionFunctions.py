
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import copy

# variable T should be in years!! (i.e. 365 days should be passed in as 1)

# calculate option's price using Block-Scholes Model, given the relevant variables
def blackScholes(r, S, K, T, sigma, contract_type):
    d1 = (  np.log(S/K) + (r+((sigma**2)/2)) *T ) / ( sigma*np.sqrt(T) )
    d2 = d1 - sigma*np.sqrt(T)
    try:
        if contract_type == 'c':
            price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

            return d1, d2, price

        elif contract_type == 'p':
            price = K*np.exp(-r*T)*norm.cdf(-d2, 0, 1) - S*norm.cdf(-d1, 0, 1)

            return d1, d2, price

        else:
            print("Error calculating blackScholes price: check contract type")
    except:
        print("There was an error calculating blackScholes price. Please confirm all parameters...")

def option_delta(d1, contract_type):
    if contract_type == 'c':
        return norm.cdf(d1)
    elif contract_type == 'p':
        return -norm.cdf(-d1)

def option_gamma(d1,S,T,sigma):
    return norm.pdf(d1)/(S*sigma*np.sqrt(T))

def option_vega(d1,S,T):
    return 0.01*(S*norm.pdf(d1)*np.sqrt(T))

def option_theta(d1,d2,S,K,T,r,sigma, contract_type):
    if contract_type == 'c':
        return 0.01*(-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)) - r*K*np.exp(-r*T)*norm.cdf(d2))
    elif contract_type == 'p':
        return 0.01 * (-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T))+r*K*np.exp(-r*T)*norm.cdf(-d2))

def option_rho(d2,K,T,r,contract_type):
    if contract_type == 'c':
        return 0.01 * (K * T * np.exp(-r * T) * norm.cdf(d2))
    elif contract_type == 'p':
        return 0.01 * (-K * T * np.exp(-r * T) * norm.cdf(-d2))

# calculate option's price using Bachelier's Model, given the relevant variables
def bachelier(r, S, K, T, sigma, contract_type):
    d = (S * np.exp(r*T) - K) / np.sqrt(sigma**2/(2 * r) * (np.exp(2*r*T)-1) )
    price = np.exp(-r * T) * (S * np.exp(r * T) - K) * norm.cdf(d) + np.exp(-r * T) * np.sqrt(sigma**2/(2*r) * (np.exp(2*r*T)-1) ) * norm.pdf(d)
    if contract_type == 'c':
        return price
    elif contract_type == 'p':
        return price - S + np.exp(-r * T) * K  # calculate put price using put/call parity equation
    else:
        print("Error calculating bachelier price: check contract type")




