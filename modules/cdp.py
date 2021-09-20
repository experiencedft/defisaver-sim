'''

The CDP module contains all the tools required to simulate a collateralized debt position, such as increasing or decreasing 
its leverage (boost and repay), closing the vault to calculate its lifetime profit, adding collateral or drawing more debt. 

The position is represented as an object whose methods provide all the above interactions. It can be leveraged or non leveraged.

For the purpose of this simulation, a vault is considered leveraged if part or all of the debt is used to buy more collateral.

'''

import numpy as np

class CDP():
    '''
    Attributes
    ___________

    collateral: float
        the amount of collateral in the position, in unit of the collateral asset
    debt: float
        the amountof debt of the position, in unit of the debt asset
    automated: bool
        a boolean flag indicating whether the CDP is automated
    automation_settings: dictionnary
        a dictionnary containing the automation settings
        {"repay from": ..., "repay to": ..., "boost from": ..., "boost to": ...}
    min_automation_debt: float
        the minimum debt required for automation to be enabled, in amount of debt asset
    min_ratio: float
        the minimum collateralization ratio admitted by the protocol, below which liquidation occurs
    '''

    def __init__(self, initial_collateral: float, initial_debt: float, min_ratio: float) -> None:
        '''
        min_ratio in %
        '''
        self.collateral = initial_collateral
        self.debt = initial_debt
        self.isAutomated = False
        self.automation_settings = {"repay from": 0, "repay to": 0, "boost from": 0, "boost to": 0}
        self.min_ratio = min_ratio
        # NOTE: pass this as an argument later on and include change in simulate.py and related function calls
        self.min_automation_debt = 10000

    def getCollateralizationRatio(self, price: float):
        '''
        Returns the collateralization ratio in %
        '''
        return 100*self.collateral*price/self.debt

    def changeCollateral(self, deltaCollateral: float):
        '''
        Add deltaCollateral to the position's collateral. Note: deltaCollateral may be negative.
        '''
        self.collateral += deltaCollateral
    
    def changeDebt(self, deltaDebt: float):
        '''
        Add deltaDebt to the position's debt. Note: deltaDebt may be negative.
        '''
        self.debt += deltaDebt

    def close(self, price: float) -> float:
        '''
        Close the vault by paying back all of the debt and return the amount of collateral left.
        Assumes infinite liquidity at the current price.

        Param:

        price: float
            The current price of the collateral denominated in the debt asset.
        '''
        if self.debt > 0:
            # The amount of collateral to sell to pay back the debt
            collateralToSell = self.debt/price
            self.collateral -= collateralToSell
            self.debt = 0
        return self.collateral

    def automate(self, repay_from: float, repay_to: float, boost_from: float, boost_to: float):
        '''
        Enable or update automation for a CDP with the given automation settings.

        Param:

        automation_settings: 
            each param is an automation setting in the order of repay from, repay to, 
            boost from, boost to
        '''
        assert repay_from > self.min_ratio + 10
        self.automated = True
        self.automation_settings["repay from"] = repay_from
        self.automation_settings["repay to"] = repay_to
        self.automation_settings["boost from"] = boost_from
        self.automation_settings["boost to"] = boost_to
    
    def disableAutomation(self):
        self.isAutomated = False

    def boostTo(self, target: float, price: float, gas_price_in_gwei: float, service_fee: float):
        '''
        Given the current price of the collateral asset denominated in the debt asset, check whether 
        the collateralization ratio is above threshold, and if yes, boost to the target ratio.
        A boost is defined as generating more debt from the position and buying collateral with it.

        Params:
            target: 
                target collateralization ratio (in %)
            price: 
                current price of the collateral denominated in the debt asset
            gas_price_in_gwei:
                current on-chain gas price in gwei (nanoETH)
            serice_fee: 
                current fee charged by DeFi Saver (in %)
        '''

        #Check that it's possible to boost with the desired target
        if self.debt == 0 or target/100 < self.collateral*price/self.debt:
            # Fixed estimate of 1M gas consumed by the boost operation to calculate the gas fee in 
            # ETH
            g = 1000000*gas_price_in_gwei*1e-9
            # Target collateralization ratio
            t = target/100
            c = self.collateral
            d = self.debt
            p = price
            gamma = 1 - service_fee/100
            # print("gas cost in USD: ", g*p)
            # print("gas cost limit: ", (p*c - t*d)/(5*(t - gamma) + 1))
            # Gas cost must be below 20% of the boost amount
            if p*g < (p*c - t*d)/(5*(t - gamma) + 1):
                #The gas charged to the user is capped at a price of 499 gwei
                if gas_price_in_gwei > 499:
                    g = 1000000*499*1e-9
                # Calculate debt increase (> 0)required to arrive to the target collateralization ratio
                deltaDebt = (p*c - p*g - t*d)/(t - gamma)
                # print("debt change: ", deltaDebt)
                # print("gas_cost/debt_change: ", p*g/deltaDebt)
                # Calculate corresponding collateral increase (> 0)
                deltaCollateral = (gamma*deltaDebt - p*g)/p
                # Update position
                self.debt += deltaDebt
                self.collateral += deltaCollateral
                assert self.debt > 0
                assert self.collateral > 0
                # Return True if boost took place
                return True
            else: 
                return False
        else: 
            # If boost not possible with desired parameters
            return False

    def repayTo(self, target: float, price: float, gas_price_in_gwei: float, service_fee: float): 
        '''
        Given the current price of the collateral asset denominated in the debt asset, check whether
        the collateralization ratio is below threshold, and if yes, repay to the target ratio. 
        A repay is defined as selling some of the collateral from the position to acquire more of the 
        debt asset and repay part of the debt with it.

        Params:
            target: 
                target collateralization ratio in %
            price: 
                current price of the collateral denominated in the debt asset
            gas_price_in_gwei:
                current on-chain gas price in gwei (nanoETH)
            serice_fee: 
                current fee charged by DeFi Saver (in %)
        '''
        collateralization = self.collateral*price/self.debt
        # Check that it's possible to repay with the desired target
        if self.debt == 0:
            assert False
        # The current CRatio must be below the target OR below min_ratio + 10%
        elif collateralization < target/100:
            # Fixed estimate of 1M gas consumed by the repay operation to calculate the gas fee in 
            # ETH
            g = 1000000*gas_price_in_gwei*1e-9
            # Target collateralization ratio
            t = target/100
            c = self.collateral
            d = self.debt
            p = price
            gamma = 1 - service_fee/100
            # print("gas cost in USD: ", p*g)
            # print("gas cost in ETH: ", g)
            # print("gas cost limit: ", (t*d - p*c)/(5*(gamma*t - 1) + t))
            # print("collateralization in %: ", 100*collateralization)
            # print("min repay threshold: ", self.min_ratio + 10)

            # Gas cost must be lower than 20% of repay amount OR we must be below the min repay ratio
            if 100*collateralization < self.min_ratio + 10:
                isEmergencyRepay = True
            else: 
                isEmergencyRepay = False
            if p*g < (t*d - p*c)/(5*(gamma*t - 1) - t) or isEmergencyRepay:
                if isEmergencyRepay:
                # In case of an emergency repay, this might exceed the previous 20%. In this case, cap the charged amount to 20%.
                    if p*g > (t*d - p*c)/(5*(gamma*t - 1) - t):
                        g = (1/p)*(t*d - p*c)/(5*(gamma*t - 1) - t)
                #The gas charged to the user is capped at a price of 499 gwei
                elif gas_price_in_gwei > 499:
                    g = 1000000*499*1e-9
                # Calculate collateral decrease (> 0) required to arrive to the target collateralization ratio
                deltaCollateral = (t*d + t*p*g - p*c)/(p*(gamma*t-1))
                # print("collateral change: ", deltaCollateral)
                # print("gas_cost/collateral_change: ", g/deltaCollateral)
                deltaDebt = gamma*p*deltaCollateral - p*g
                if self.debt < self.min_automation_debt :
                    self.isAutomated = False
                # Update position
                self.collateral -= deltaCollateral
                self.debt -= deltaDebt
                assert self.collateral > 0
                assert self.debt > 0
                # Return True if repay took place
                return True
            else: 
                return False
        else:
            return False