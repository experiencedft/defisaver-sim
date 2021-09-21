'''
Simulation toolbox for automated, fully leveraged vaults.
'''

import json
from datetime import datetime
from pathlib import Path

from typing import Tuple
from modules.cdp import CDP
from modules.pricegeneration import generateGBM, generateBoundedGBM

# NOTE: The max losses are not well defined, what we actually need to do is extract the peaks of the values 
# arrays, and return the max fall in % from peak to peak

def simulateLeveragedSingle(init_portfolio_value, init_collateralization, min_ratio, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, price_path, save_results = False):
    '''
    Simulate a leveraged automated vault with a single price path. This function has no
    concept of time, it just loops through the provided price array and triggers boost or 
    repay when applicable. If the vault's debt value falls below the min debt for DeFi Saver,
    it is closed to the collateral asset. 

    Params:

    init_portfolio_value: float
        initial value of the portfolio *before* opening the collateralized debt position (CDP), 
        denominated in the collateral asset.
    init_collateralization: float
        desired initial collateralization for the CDP. Note: it will be fully leveraged at that
        collateralization ratio.
    repay_from: float
    repay_to: float
    boost_from: float
    boost_to: float
        the automation settings, i.e. the thresholds at which a rebalancing must be triggered and the 
        respective targets. In %.
    service_fee: float
        fee charged from the automated rebalancing protocol in % of the rebalanced amount.
    gas_price: float
        average gas price throughout the simulation. NOTE: improve to include gas price array later on
    price_path: list
        the price path to simulate, no notion of time is needed

    Returns: 

    values_in_collateral: list
        the list of values of the vault denominated in collateral throughout the simulation
    values_in_debt: list
        the list of values of the vault denominated in debt asset throughout the simulation
    collateralizations: list 
        the list of collateralizations of the vault throughout the simulation
    '''
    # Create vault and fill it with the entire portfolio value
    vault = CDP(init_portfolio_value, 0, min_ratio)
    # Leverage the vault to the target collateralization at the initial price
    vault.boostTo(init_collateralization, price_path[0], 0, 0)
    vault.automate(repay_from, repay_to, boost_from, boost_to)
    values_in_collateral = [init_portfolio_value]
    values_in_debt = [init_portfolio_value*price_path[0]]
    collateralizations = [init_collateralization]
    for price in price_path: 
        # If the vault is automated, repay or boost if needed
        if vault.isAutomated:
            if vault.getCollateralizationRatio(price) > vault.automation_settings["boost from"]:
                _ = vault.boostTo(vault.automation_settings["boost to"], price, gas_price, service_fee)
            elif vault.getCollateralizationRatio(price) < vault.automation_settings["repay from"]:
                _ = vault.repayTo(vault.automation_settings["repay to"], price, gas_price, service_fee)
                # If the vault falls below the min debt for automation, close it to collateral
                if not(vault.isAutomated):
                    vault.close(price)
        # print("Current price: ", price)
        # print("Current collateral: ", vault.collateral)
        # print("Current collateral value: ", vault.collateral*price)
        # print("Current debt: ", vault.debt)
        # print("Current collateralization: ", vault.getCollateralizationRatio(price))
        # if vault.isAutomated: 
        #     print("Vault is automated: YES", "\n")
        # else: 
        #     print("Vault is automated: NO", "\n")
        assert vault.collateral > vault.debt/price
        values_in_collateral.append(vault.collateral - vault.debt/price)
        values_in_debt.append(price*(vault.collateral - vault.debt/price))
        if vault.debt > 0: 
            collateralizations.append(vault.getCollateralizationRatio(price))
        else: 
            collateralizations.append(0)

    if save_results == True: 
        data = {}
        data['values_in_collateral'] = values_in_collateral
        data['values_in_debt'] = values_in_debt
        data['collateralizations'] = collateralizations
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        filename = 'single_lev_sim' + dt_string + '.dat'
        Path('sim_results').mkdir(parents=True, exist_ok=True)
        with open('sim_results/'+filename, 'w+') as f:
            json.dump(data, f)

    return values_in_collateral, values_in_debt, collateralizations


def simulateLeveragedBoundedGBM(init_portfolio_value, init_collateralization, min_ratio, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, N_paths, volatility, start_price, end_price, time_horizon = 1, time_step_size = 0.000456621, save_results = False):
    '''
    Simulate a sample of price paths for an automated leveraged vault when the user has 
    a particular expectation of the price appreciation (or depreciation) of the collateral 
    asset within a certain timeframe, as well as the volatility along the way.

    Params:

    init_portfolio_value: float
        initial value of the portfolio *before* opening the collateralized debt position (CDP), 
        denominated in the collateral asset.
    init_collateralization: float
        desired initial collateralization for the CDP. Note: it will be fully leveraged at that
        collateralization ratio.
    repay_from: float
    repay_to: float
    boost_from: float
    boost_to: float
        the automation settings, i.e. the thresholds at which a rebalancing must be triggered and the 
        respective targets. In %.
    service_fee: float
        fee charged from the automated rebalancing protocol in % of the rebalanced amount.
    gas_price: float
        average gas price throughout the simulation. NOTE: improve to include gas price array later on
    N_paths: int
        the number of random paths to average over
    volatility: float
        the annualized volatility to generate the price paths with, in decimal units
    start_price: float
        the start price of the bounded GBMs
    end_price: float
        the end price of the bounded GBMs
    time_horizon: float
        the number of years covered by the simulation. can be lower than 1.
    time_steps_size: float
        size of the time steps of the simulation, in years. can be lower than 1

    Returns: 
    
    returns_in_collateral_asset: list
        the array of returns denominted in collateral for each price path as a multiplier of the 
        initial amount of collateral in the portfolio
    returns_in_debt_asset: list
        the array of returns denominated in debt asset for each price path as a multiplier of the 
        initial amount of the debt asset the portfolio was worth
    max_loss_debt: list
        the maximum loss in % denominated in the debt asset for each price path
    '''
    # Arrays to record the overall returns and max loss denominated in debt for each path
    # Returns are a multiple of the initial value
    returns_in_collateral_asset = []
    returns_in_debt_asset = []
    # Max loss is in %
    max_losses_in_collateral_asset = []
    max_losses_in_debt_asset = []
    # Simulate the N_paths paths and record their overall returns
    for _ in range(N_paths):
        _, path = generateBoundedGBM(time_horizon, volatility, start_price, end_price, time_step_size)
        values_in_collateral, values_in_debt, _ =  simulateLeveragedSingle(init_portfolio_value, init_collateralization, min_ratio, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, path)
        returns_in_collateral_asset.append(values_in_collateral[-1]/values_in_collateral[0])
        returns_in_debt_asset.append(values_in_debt[-1]/values_in_debt[0])
        max_losses_in_collateral_asset.append(100*(1- min(values_in_collateral)/max(values_in_collateral)))
        max_losses_in_debt_asset.append(100*(1- min(values_in_debt)/max(values_in_debt)))

    if save_results == True: 
        data = {}
        data['returns_in_collateral_asset'] = returns_in_collateral_asset
        data['returns_in_debt_asset'] = returns_in_debt_asset
        data['max_losses_in_collateral_asset'] = max_losses_in_collateral_asset
        data['max_losses_in_debt_asset'] = max_losses_in_debt_asset
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        filename = 'bounded_gbm_sim' + dt_string + '.dat'
        Path('sim_results').mkdir(parents=True, exist_ok=True)
        with open('sim_results/'+filename, 'w+') as f:
            json.dump(data, f)

    return returns_in_collateral_asset, returns_in_debt_asset, max_losses_in_collateral_asset, max_losses_in_debt_asset


def simulateLeveragedGBM(init_portfolio_value, init_collateralization, min_ratio, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, N_paths, volatility, drift, init_price, time_horizon = 1, time_step_size = 0.000456621, save_results = False) -> Tuple[list, list, list]: 
    '''
    Simulate a sample of price paths for an automated leveraged vault when the user 
    has a particular expectation of the annual growth rate of the average annual growth 
    rate of the asset.

    Params:

    init_portfolio_value: float
        initial value of the portfolio *before* opening the collateralized debt position (CDP), 
        denominated in the collateral asset.
    init_collateralization: float
        desired initial collateralization for the CDP. Note: it will be fully leveraged at that
        collateralization ratio.
    repay_from: float
    repay_to: float
    boost_from: float
    boost_to: float
        the automation settings, i.e. the thresholds at which a rebalancing must be triggered and the 
        respective targets. In %.
    service_fee: float
        fee charged from the automated rebalancing protocol in % of the rebalanced amount.
    gas_price: float
        average gas price throughout the simulation. NOTE: improve to include gas price array later on
    N_paths: int
        the number of random paths to average over
    volatility: float
        the annualized volatility to generate the price paths with, in decimal units
    drift: float
        the annualized log growth rate for the asset
    time_horizon: float
        the number of years covered by the simulation. can be lower than 1.
    time_steps_size: float
        size of the time steps of the simulation, in years. can be lower than 1

    Returns: 
    
    returns_in_collateral_asset: list
        the array of returns denominted in collateral for each price path as a multiplier of the 
        initial amount of collateral in the portfolio
    returns_in_debt_asset: list
        the array of returns denominated in debt asset for each price path as a multiplier of the 
        initial amount of the debt asset the portfolio was worth
    max_loss_in_collateral_asset: list
        the maximum loss in % denominated in the collateral asset for each price path
    max_loss_debt_asset: list
        the maximum loss in % denominated in the debt asset for each price path
    '''
    # Arrays to record the overall returns and max loss denominated in debt for each path
    # Returns are a multiple of the initial value
    returns_in_collateral_asset = []
    returns_in_debt_asset = []
    # Max loss is in %
    max_losses_in_collateral_asset = []
    max_losses_in_debt_asset = []
    # Simulate the N_paths paths and record their overall returns
    for _ in range(N_paths):
        _, path = generateGBM(time_horizon, drift, volatility, init_price, time_step_size)
        values_in_collateral, values_in_debt, _ =  simulateLeveragedSingle(init_portfolio_value, init_collateralization, min_ratio, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, path)
        returns_in_collateral_asset.append(values_in_collateral[-1]/values_in_collateral[0])
        returns_in_debt_asset.append(values_in_debt[-1]/values_in_debt[0])
        max_losses_in_collateral_asset.append(100*(1- min(values_in_collateral)/max(values_in_collateral)))
        max_losses_in_debt_asset.append(100*(1- min(values_in_debt)/max(values_in_debt)))

    if save_results == True: 
        data = {}
        data['returns_in_collateral_asset'] = returns_in_collateral_asset
        data['returns_in_debt_asset'] = returns_in_debt_asset
        data['max_losses_in_collateral_asset'] = max_losses_in_collateral_asset
        data['max_losses_in_debt_asset'] = max_losses_in_debt_asset
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        filename = 'gmb_sim' + dt_string + '.dat'
        Path('sim_results').mkdir(parents=True, exist_ok=True)
        with open('sim_results/'+filename, 'w+') as f:
            json.dump(data, f)

    return returns_in_collateral_asset, returns_in_debt_asset, max_losses_in_collateral_asset, max_losses_in_debt_asset
