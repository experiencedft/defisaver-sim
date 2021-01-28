import sys
import numpy as np
import matplotlib.pyplot as plt 

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


    if d == 0:
        ratio = float("inf")
    else:
        ratio = collateral_value/vault["debt"]

    #print("Current ratio: ", ratio)

    if ratio >= vault["boost from"]/100:
        #Algebra to get required debt change to reach a target ratio
        debt_change = (p*c - (1-s)*g - t*d)/(t - (1-s))
        #print("Required debt change: ", debt_change)
        #If gas fee lower than 5% boost amount, convert newly generated debt, subtract gas fee and service fee, and add to collateral
        #print("Amount to swap for boosting: ", (1-service_fee)*(debt_change - g))
        #print("Gas cost: ", g)
        if g < 0.05*debt_change*(1-s)/(2-s) or ratio < 1.65: 
            vault["collateral"] += (1- s)*(debt_change-g)/p
            #Add newly generated debt
            vault["debt"] += debt_change
            # print("Boosted! New ratio = ", p*vault["collateral"]/vault["debt"], "\n")
            # print("Vault: ", vault, "\n")
        #else: 
            #print("No boost :(\n") 

    return vault 

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


    if d == 0:
        ratio = float("inf")
    else: 
        ratio = collateral_value/vault["debt"]
    
    if ratio <= vault["repay from"]/100:
        #Algebra to get required collateral change to reach a target ratio
        collateral_change = (p*c + t*s*g - t*d - t*g)/(p - t*p + t*s*p)
        #If gas fee lower than 5% repay amount, convert extracted collateral and swap to repay debt
        # print("Amount to swap for boosting: ", (1 - s)*(p*collateral_change - g))
        # print("Gas cost: ", g)
        if g < 0.05*p*collateral_change*(1-s)/(1.05 - 0.05*s) or ratio < 1.65:
            #Remove collateral
            vault["collateral"] -= collateral_change
            #Convert collateral to DAI and substract from debt
            vault["debt"] -= (1 - s)*(p*collateral_change - g)
            #print("Repayed! New ratio: ", p*vault["collateral"]/(vault["debt"]), "\n")
        #else: 
            # print("Current ratio: ", ratio)
            # print("No repay :(\n")

    return vault

def close(vault, eth_price):
    '''
    Given a vault (dictionary), returns the collateral that would be left by closing it using the collateral within the vault to repay the debt.

        Parameters: 
            vault (dictionary): A dictionary representing an automated vault
            eth_price (float): A float representing the current price of ETH

        Returns: 
            balance (float): The current vault's balance (what would be left after closing it)
            profit_in_collateral (float): The net profit of the vault, denominated in collateral. IF SOME DEBT WAS INITIALLY EXTRACTED, IT IS COUNTED AS LOST. 
    '''
    collateral_to_repay_debt = vault["debt"]/eth_price
    balance = vault["collateral"] - collateral_to_repay_debt
    profit_in_collateral = balance - vault["initial collateral"]

    return balance, profit_in_collateral

def createUptrend(init_price, final_price, n_corrections,  amplitude_list):
    '''
    Returns a numpy array representing an uptrend. Here,  uptrend is defined as a final price higher than the initial price, with the possibility of a user specified number of corrections with user specified amplitudes along the way. 

    Parameters:
        init_price (float): Initial price.
        final_price (float): Final price.
        n_corrections (int): Number of corrections along the way.
        amplitude_list (list): List giving the amplitude of each correction. Should be of length n_corrections with values between 0 and 100 (percentages)
    
    Returns: 
        priceArray (numpy array): Array of length 1000*(n_corrections + 1) representing the price action to ensure granularity even over very long price ranges.
    '''
    #Verification of user specified inputs
    if (init_price <= 0 or final_price <= 0): 
        sys.exit("Error: Please use strictly positive prices.")
    elif (final_price <= init_price):
        sys.exit("Error: Please enter a final price higher than the initial price, or use the createBearPriceAction function instead.")
    elif (not all(0 < amplitude < 100 for amplitude in amplitude_list )):
        sys.exit("Error: Please provide correction amplitude values strictly comprised between 0 and 100 (%)")
    elif (len(amplitude_list) != n_corrections):
        sys.exit("Error: The length of the corrections amplitude list should be equal to the number of corrections")
    #Straight line between the initial and final price
    init_array = np.linspace(init_price, final_price, 1000)
    if n_corrections != 0:
        #Get an array of n_corrections evenly spaced intermediate values from this initial line
        indices = np.round(np.linspace(1, len(init_array) - 2, n_corrections)).astype(int)
        correction_thresholds = init_array[indices]
        #These values are used as the thresholds at which a user specified correction is triggered. 
        local_extrema = []
        for i in range(len(correction_thresholds) - 1):
            element = correction_thresholds[i]
            correction = amplitude_list[i]
            corrected_element = element*(1 - correction/100)
            local_extrema.append(element)
            local_extrema.append(corrected_element)
        #Create a 1000 sized linspace between each of the found values to get the desired price action
        local_extrema.insert(0, init_array[0])
        local_extrema.append(init_array[len(init_array)-1])
        priceArray = np.array([])
        for i in range(len(local_extrema)-1):
            segment = np.linspace(local_extrema[i], local_extrema[i+1],1000)
            priceArray = np.append(priceArray, segment)
    else: 
        priceArray = init_array
    return priceArray

def createDowntrend(init_price, final_price, n_bounces, amplitude_list): 
    '''
    Returns a numpy array representing a downtrend. Here, downtrend is defined as a final price lower than the initial price, with the possibility of a user specified number of bounces with user specified amplitudes along the way. 

    Parameters:
        init_price (float): Initial price.
        final_price (float): Final price.
        n_bounces (int): Number of bounces along the way.
        amplitude_list (list): List giving the amplitude of each bounce. Should be of length n_bounces with values between 0 and 100 (percentages)
    
    Returns: 
        priceArray (numpy array): Array of length 1000*(n_bounces + 1) representing the price action to ensure granularity even over very long price ranges.
    '''
    #Verification of user specified inputs
    if (init_price <= 0 or final_price <= 0): 
        sys.exit("Error: Please use strictly positive prices.")
    elif (final_price >= init_price):
        sys.exit("Error: Please enter a final price lower than the initial price, or use the createBullPriceAction function instead.")
    elif (not all(0 < amplitude < 100 for amplitude in amplitude_list )):
        sys.exit("Error: Please provide bounce amplitude values strictly comprised between 0 and 100 (%)")
    elif (len(amplitude_list) != n_bounces):
        sys.exit("Error: The length of the bounces amplitude list should be equal to the number of bounces")
    #Straight line between the initial and final price
    init_array = np.linspace(init_price, final_price, 1000)
    if n_bounces != 0: 
        #Get an array of n_bounces evenly spaced intermediate values from this initial line
        indices = np.round(np.linspace(1, len(init_array) - 2, n_bounces)).astype(int)
        bounce_thresholds = init_array[indices]
        #These values are used as the thresholds at which a user specified bounce is triggered. 
        local_extrema = []
        for i in range(len(bounce_thresholds) - 1):
            element = bounce_thresholds[i]
            bounce = amplitude_list[i]
            bounced_element = element*(1 + bounce/100)
            local_extrema.append(element)
            local_extrema.append(bounced_element)
        #Create a 1000 sized linspace between each of the found values to get the desired price action
        local_extrema.insert(0, init_array[0])
        local_extrema.append(init_array[len(init_array)-1])
        priceArray = np.array([])
        for i in range(len(local_extrema)-1):
            segment = np.linspace(local_extrema[i], local_extrema[i+1],1000)
            priceArray = np.append(priceArray, segment)
    else: 
        priceArray = init_array
    return priceArray
    
def createSideways(average_price, amplitude, n_cycles):
    ''' 
    Returns a numpy array representing a sideways price action. Here, sideways is defined as the going up and down above an average price, starting at that average and coming back to it in one or more cycles with an amplite define in percentage of the average.

    Parameters:
        average_price (float): Average price, which is also the initial price here.
        amplitude (float): Amplitude in %, that is the price will move by +/- amplitude% from the average price.
        n_cycles (int): Number of cycles. Given an amplitude of X%, one cycle means the price goes +X%, back to the initial price, -X% from there, and back to the initial price again. 
        '''
    amplitude = amplitude/100
    x = np.linspace(0, 1, 1000)
    priceArray = average_price*(1+amplitude*np.sin(2*n_cycles*np.pi*x))

    return priceArray

#Let the user simulate as many vaults as they wish
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
        priceArray = createUptrend(init_price, final_price, n_corrections, amplitude_list)
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
        priceArray = createDowntrend(init_price, final_price, n_bounces, amplitude_list)
    elif market_trend == "3":
        average_price = float(input("Enter the average that the price is moving around: "))
        amplitude = float(input("Enter the amplitude of the ups and downs from the average in %: "))
        n_cycles = int(input("Enter the number of cycles of the sideways market (1 cycle = starts from the average, goes up by amplitude%, goes back to the average, goes down by amplitude%, and goes back to the average): "))
        priceArray = createSideways(average_price, amplitude, n_cycles)


    vault = {"collateral": init_collateral, "debt": init_debt, "repay from": repay_from, "repay to": repay_to, "boost from": boost_from, "boost to": boost_to, "initial collateral": init_collateral, "initial debt": init_debt}

    print("Plotting selected price action...\n")

    print("Close the plot window to continue.")

    plt.plot(priceArray)
    plt.show()

    print("Simulating vault behavior...\n")

    for price in priceArray:
        vault = boost(vault, price, gas_price, service_fee)
        vault = repay(vault, price, gas_price, service_fee)


    balance, profit = close(vault, priceArray[len(priceArray) - 1])

    print("Vault ETH balance: ", balance)
    print("Vault profit:  ", profit)
    
    cont = input("Do you wish to run another simulation? Y/N  ")

    if cont == "N":
        break 