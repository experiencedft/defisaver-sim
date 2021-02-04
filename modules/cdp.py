'''

The CDP module contains all the tools required to act on a Maker collateralized debt position or vault, such as increasing or decreasing its leverage (boost and repay), closing the vault to calculate its lifetime profit, adding collateral or drawing more debt. 

The vault should be presented to the interface as a Python dictionary with the appropriate keys depending on the function called. The keys should be:

"collateral": The collateral in the vault.
"debt": The debt associated with the vault.
"repay from": The collateralization threshold in % at which the vault should automatically be deleveraged.
"repay to": The collateralization target in % after deleveraging.
"boost from": The collateralization threshold in % at which the leverage of the vault should automatically be increased. 
"boost to": The collateralization target in % after increasing leverage.
"initial collateral": The initial collateral in at the inception of the vault.
"initial debt": The initial debt at the inception of the vault. 

'''

import numpy as np

def boost(vault, eth_price, gas_price, service_fee):
    '''
    Given a vault (dictionary), checks if the vault can be boosted, and if yes, boosts it and returns the new vault.

        Parameters: 
            vault (dictionary): A dictionary representing an automated vault
            eth_price (float): A float representing the current price of ETH - or another collateral
            gas_price (float): A float representing the current *fast* gas price in gwei
            service_fee (float): A float representing the DeFi Saver service fee in %

        Returns: 
            vault (dictionary): The new updated vault
    '''  
    collateral_value = vault["collateral"]*eth_price
    gas_fee_in_eth = 800000*gas_price*1e-9
    gas_fee_in_usd = eth_price*gas_fee_in_eth
    #Conversion of service fee in decimal format
    s = service_fee/100
    #New variables for more readable math
    p = eth_price
    c = vault["collateral"]
    g = gas_fee_in_usd
    t = vault["boost to"]/100 #Must be in decimal format in the code
    d = vault["debt"]
    boosted = False

    if d == 0:
        ratio = float("inf")
    else:
        ratio = collateral_value/vault["debt"]

    if ratio >= vault["boost from"]/100:
        #Algebra to get required debt change to reach a target ratio
        debt_change = (p*c - (1-s)*g - t*d)/(t - (1-s))
        #If gas fee lower than 5% boost amount, convert newly generated debt, subtract gas fee and service fee, and add to collateral
        if g < 0.05*debt_change*(1-s)/(2-s) or ratio < 1.65: 
            vault["collateral"] += (1- s)*(debt_change-g)/p
            #Add newly generated debt
            vault["debt"] += debt_change
            boosted = True

    return vault, boosted

def repay(vault, eth_price, gas_price, service_fee):
    '''
    Given a vault (dictionary), checks if the vault can be repayed, and if yes, repays it and returns the new vault.

        Parameters: 
            vault (dictionary): A dictionary representing an automated vault
            eth_price (float): A float representing the current price of ETH 
            gas_price (float): A float representing the current *fast* gas price in gwei
            service_fee (float): A float representing the DeFi Saver service fee in %

        Returns: 
            vault (dictionary): The new updated vault
    '''  
    collateral_value = vault["collateral"]*eth_price
    gas_fee_in_eth = 800000*gas_price*1e-9
    gas_fee_in_usd = eth_price*gas_fee_in_eth
    #Conversion of service fee in decimal format
    s = service_fee/100
    #New variables for more readable math
    p = eth_price
    c = vault["collateral"]
    g = gas_fee_in_usd
    t = vault["repay to"]/100 #Must be in decimal format in the code
    d = vault["debt"]
    repaid = False

    if d == 0:
        ratio = float("inf")
    else: 
        ratio = collateral_value/vault["debt"]
    
    if ratio <= vault["repay from"]/100:
        #Algebra to get required collateral change to reach a target ratio
        collateral_change = (p*c + t*s*g - t*d - t*g)/(p - t*p + t*s*p)
        #If gas fee lower than 5% repay amount, convert extracted collateral and swap to repay debt
        if g < 0.05*p*collateral_change*(1-s)/(1.05 - 0.05*s) or ratio < 1.65:
            #Remove collateral
            vault["collateral"] -= collateral_change
            #Convert collateral to DAI and substract from debt
            vault["debt"] -= (1 - s)*(p*collateral_change - g)
            repaid = True

    return vault, repaid

def close(vault, eth_price):
    '''
    Given a vault (dictionary), returns the collateral that would be left by closing it using the collateral within the vault to repay the debt.

        Parameters: 
            vault (dictionary): A dictionary representing an automated vault
            eth_price (float): A float representing the current price of ETH

        Returns: 
            balance (float): The current vault's balance (what would be left after closing it)
            profit_in_collateral (float): The net profit of the vault, denominated in collateral. 
    '''
    collateral_to_repay_debt = vault["debt"]/eth_price
    balance = vault["collateral"] - collateral_to_repay_debt
    profit_in_collateral = balance - vault["initial balance"]

    return balance, profit_in_collateral