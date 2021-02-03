'''

A command line script to let the user simulate an automated DeFi Saver vault with using some simplified price action profiles based only on linear interpolation between local maxima. 

'''

import numpy as np
import matplotlib.pyplot as plt
from modules import cdp 
from modules import pricegeneration as pr

#Loop until the user decides to stop simulating vaults.
while True: 

    init_collateral = float(input("Enter the initial amount of ETH to put in the vault: "))
    init_debt = float(input("Enter the initial debt withdrawn (0 if leveraged vault): "))

    print("\n Automation settings in % collateralization\n")

    repay_from = float(input("Repay from: "))
    repay_to = float(input("Repay to: "))
    boost_from = float(input("Boost from: "))
    boost_to = float(input("Boost to: "))

    print("\n Market conditions for the simulation \n")

    gas_price =  float(input("Enter a fast gas price which will be used for the simulation (in gwei): ")) #in gwei
    service_fee = float(input("Enter the DeFi Saver service fee to use for automation in %: ")) #in %, currently at 0.3%

    while True: 
        market_trend = input("Choose a market trend from uptrend, downtrend or sideways by entering 1, 2 or 3: ")
        if market_trend in ["1", "2", "3"]:
            break
        else: 
            print("Please enter 1, 2 or 3")

    if market_trend == "1":
        while True: 
            init_price = float(input("Initial price in USD: "))
            final_price = float(input("Final price in USD: "))
            if init_price < final_price:
                break
            else:
                print("The initial price should be lower than the final price")
        while True: 
            n_corrections = int(input("Number of corrections (0 if no correction): "))
            amplitude_list = input("Amplitude of corrections in %, separated by a comma - Press ENTER if you selected 0 corrections: ")
            #Convert to list of floats
            if amplitude_list == "":
                amplitude_list = []
            else:
                amplitude_list = [float(i) for i in amplitude_list.split(",")]
            if n_corrections == len(amplitude_list): 
                break
            else: 
                print("The number of corrections should be equal to the length of the list of corrections")
        priceArray = pr.createUptrend(init_price, final_price, n_corrections, amplitude_list)
    elif market_trend == "2": 
        while True: 
            init_price = float(input("Initial price in USD: "))
            final_price = float(input("Final price in USD: "))
            if init_price > final_price:
                break
            else:
                print("The final price should be lower than the initial price")
        while True: 
            n_bounces = int(input("Number of bounces (0 if no bounces): "))
            amplitude_list = input("Amplitude of bounces in %, separated by a comma - Press ENTER if you selected 0 bounces: ")
            if amplitude_list == "":
                amplitude_list = []
            else: 
                amplitude_list = [float(i) for i in amplitude_list.split(",")]
            if n_bounces == len(amplitude_list): 
                break
            else: 
                print("The number of bounces should be equal to the length of the list of bounces")
        priceArray = pr.createDowntrend(init_price, final_price, n_bounces, amplitude_list)
    elif market_trend == "3":
        average_price = float(input("Enter the average that the price is moving around: "))
        amplitude = float(input("Enter the amplitude of the ups and downs from the average in %: "))
        n_cycles = int(input("Enter the number of cycles of the sideways market (1 cycle = starts from the average, goes up by amplitude%, goes back to the average, goes down by amplitude%, and goes back to the average): "))
        priceArray = pr.createSideways(average_price, amplitude, n_cycles)


    vault = {"collateral": init_collateral, "debt": init_debt, "repay from": repay_from, "repay to": repay_to, "boost from": boost_from, "boost to": boost_to, "initial collateral": init_collateral, "initial debt": init_debt}

    print("Plotting selected price action...\n")

    print("Close the plot window to continue.")

    plt.plot(priceArray)
    plt.show()

    print("Simulating vault behavior...\n")

    for price in priceArray:
        vault = cdp.boost(vault, price, gas_price, service_fee)[0]
        vault = cdp.repay(vault, price, gas_price, service_fee)[0]


    balance, profit = cdp.close(vault, priceArray[len(priceArray) - 1])

    print("Vault ETH balance: ", balance)
    print("Vault profit:  ", profit)
    
    cont = input("Do you wish to run another simulation? Y/N  ")

    if cont == "N":
        break 