'''
Obtain the optimal constant leverage factor in the continuous limit assuming a given time period, volatility, 
and underlying return. 
'''

import numpy as np 
from scipy.optimize import minimize_scalar

def computeConstantLeverageReturn(leverage_ratio, underlying_return, time_period, volatility):
    '''
    Compute the return from the constant leverage strategy assuming no cost to borrow and no management fee.

    params: 

    leverage_ratio: 
        the desired constant leverage ratio
    underlying_return: 
        return of the underlying asset as a multiple of initial price
    time_period: 
        time period in years
    volatility: 
        average annualized volatility over the time period
    '''
    l = leverage_ratio
    t = time_period
    vol = volatility
    return (underlying_return**l)*np.exp(((l-l**2)/2)*vol*t)

def optimizeFactorContinuous(underlying_return, time_period, volatility):
    def computeReturn(leverage_ratio):
        return -computeConstantLeverageReturn(leverage_ratio, underlying_return, time_period, volatility)
    sol = minimize_scalar(computeReturn)
    return sol.x, abs(sol.fun)