''' 

The Price Generation module is a toolkit to generate price actions which are simplistic, time independent, local extrema based profiles.  

'''

import sys
import numpy as np

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