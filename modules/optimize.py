'''
Obtain the optimal constant leverage ratio in the continuous limit assuming a given time period, volatility, 
and underlying return. 
'''

import numpy as np 
from scipy.optimize import minimize_scalar, minimize

from modules.simulate import simulateLeveragedBoundedGBM

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
    return (underlying_return**l)*np.exp(((l-l**2)/2)*(vol**2)*t)

def optimizeRatioContinuous(underlying_return, time_period, volatility):
    '''
    Given some basic market conditions, compute the leverage ratio that maximizes the return 
    denominated in the debt asset.

    If the solution is below 1, return 1 as it means leveraging can only decrease returns.

    params:

    underlying_return: 
        return of the underlying asset as a multiple of initial price
    time_period: 
        time period in years
    volatility: 
        average annualized volatility over the time period

    returns: 
        
    sol: 
        the optimal leverage ratio
    return: 
        the corresponding return
    '''
    def computeReturn(leverage_ratio):
        return -computeConstantLeverageReturn(leverage_ratio, underlying_return, time_period, volatility)
    sol = minimize_scalar(computeReturn)
    if sol.x < 1:
        return 1, computeConstantLeverageReturn(1, underlying_return, time_period, volatility)
    return sol.x, abs(sol.fun)

def optimizeAutomationBoundedGBM(initial_portfolio_value, min_ratio, service_fee, gas_price, volatility, start_price, end_price, time_horizon):
    '''
    Given some real world parameters for DeFi Saver, average gas conditions, and user specified
    expectations of start price, end price and volatility for the collateral asset, compute the  
    optimal choice of admissible automation settings to maximizes the expected return. If the expected 
    return is less than the return of the underlying, return an empty list, signifying that automation
    is not a good choice.
    '''

    # Constraint functions

    # Repay from must be 10% greater than min ratio.
    def constraint0(x):
        return x[0] - min_ratio - 10.1
    # Repay to must be 5% greater than repay from 
    def constraint1(x):
        return x[1] - x[0] - 5
    # Boost to must be 5% greater than repay to
    def constraint2(x):
        return x[3] - x[1] - 5
    # Boost from must be 5% greater than boost to
    def constraint3(x):
        return x[2] - x[3] - 5
    # Boost from must be lower than 1000%
    def constraint4(x):
        return 1000 - x[2]


    cons0 = {'type': 'ineq', 'fun': constraint0}
    cons1 = {'type': 'ineq', 'fun': constraint1}
    cons2 = {'type': 'ineq', 'fun': constraint2}
    cons3 = {'type': 'ineq', 'fun': constraint3}
    cons4 = {'type': 'ineq', 'fun': constraint4}
    cons = [cons0, cons1, cons2, cons3, cons4]

    def meanReturnBoundedGBM(automation_settings):
        '''
        Opposite of mean return since the optimization routine is a minimization routine.
        Simulations start at a leverage corresponding to the the "boost to" target.
        '''
        repay_from = automation_settings[0]
        repay_to = automation_settings[1]
        boost_from = automation_settings[2]
        boost_to = automation_settings[3]
        print("Trying values: ")
        print("Repay from: ", repay_from)
        print("Repay to: ", repay_to)
        print("Boost from: ", boost_from)
        print("Boost to: ", boost_to, "\n")
        return_in_collateral_asset, _, _, _ = simulateLeveragedBoundedGBM(initial_portfolio_value, boost_to, min_ratio, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, 200, volatility, start_price, end_price, time_horizon, 0.000114155)
        return -np.mean(return_in_collateral_asset)

    # Look for the optimal leverage ratio in the continuous case to have a good initial guess.
    L, _ = optimizeRatioContinuous(end_price/start_price, time_horizon, volatility)
    R_init = 100*L/(L-1)
    print("Optimal L in continuous case: ", L)
    print("Corresponding ratio: ", R_init)
    if R_init < min_ratio + 10:
        initial_guess = [200, 220, 240, 220]
    else: 
        initial_guess = [R_init - 5, R_init, R_init + 5, R_init]
    # Actual optimization routine
    res = minimize(meanReturnBoundedGBM, initial_guess, constraints = cons, method='COBYLA', options={'catol': 0}, tol=0.1)
    sol = res.x
    repay_from = sol[0]
    repay_to = sol[1]
    boost_from = sol[2]
    boost_to = sol[3]
    returns, _, _, _ = simulateLeveragedBoundedGBM(initial_portfolio_value, boost_to, min_ratio, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, 100, volatility, start_price, end_price, time_horizon, 0.000114155)
    optimal_expected_return_in_collateral = np.mean(returns)
    if optimal_expected_return_in_collateral < 1:
        return [0, 0, 0, 0], 1
    return sol, optimal_expected_return_in_collateral