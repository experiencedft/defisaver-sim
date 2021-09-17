''' 

The Price Generation module is a toolkit to generate price various price action profiles from simple linear interpolation to random walks with prescribed variance.  

'''

import sys
import numpy as np

def createUptrend(init_price, final_price, n_corrections,  amplitude_list):
    '''
    Returns a numpy array representing an uptrend. Here,  uptrend is defined as a final price higher than the initial price, with the possibility of a user specified number of corrections with user specified amplitudes along the way. A simple interpolation between local maxima is used. 1000 sized array with no reference to time. 

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
        indices = np.round(np.linspace(1, len(init_array) - 2, n_corrections+2)).astype(int)
        indices = indices[1:]
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
    A simple interpolation between local maxima is used. 1000 sized array with no reference to time.  

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
        indices = np.round(np.linspace(1, len(init_array) - 2, n_bounces+2)).astype(int)
        indices = indices[1:]
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
    Returns a numpy array representing a sideways price action. Here, sideways is defined as the going up and down above an average price, starting at that average and coming back to it in one or more cycles with an amplite define in percentage of the average. Simple sine wave, no reference to time.

    Parameters:
        average_price (float): Average price, which is also the initial price here.
        amplitude (float): Amplitude in %, that is the price will move by +/- amplitude% from the average price.
        n_cycles (int): Number of cycles. Given an amplitude of X%, one cycle means the price goes +X%, back to the initial price, -X% from there, and back to the initial price again. 
        '''
    amplitude = amplitude/100
    x = np.linspace(0, 1, 1000)
    priceArray = average_price*(1+amplitude*np.sin(2*n_cycles*np.pi*x))

    return priceArray

def boundedRandomWalk(length, lower_bound,  upper_bound, start, end, std):
    '''

    Taken from user igrinis on Stack Overflow: https://stackoverflow.com/a/47005958/5433929

    From the post:

    You can see it as a solution of geometric problem. 
    The trend_line is connecting your start and end points, and have margins defined by lower_bound and upper_bound. 
    rand is your random walk, rand_trend it's trend line and rand_deltas is it's deviation from the rand trend line. 
    We collocate the trend lines, and want to make sure that deltas don't exceed margins. When rand_deltas exceeds the allowed margin, we "fold" the excess back to the bounds.
    At the end you add the resulting random deltas to the start=>end trend line, thus receiving the desired bounded random walk.
    The std parameter corresponds to the amount of variance of the random walk.
    In this version "std" is not promised to be the "interval". 


    '''
    assert (lower_bound <= start and lower_bound <= end)
    assert (start <= upper_bound and end <= upper_bound)

    bounds = upper_bound - lower_bound

    rand = (std * (np.random.random_sample(length) - 0.5)).cumsum()
    rand_trend = np.linspace(rand[0], rand[-1], length)
    rand_deltas = (rand - rand_trend)
    rand_deltas /= np.max([1, (rand_deltas.max()-rand_deltas.min())/bounds])

    trend_line = np.linspace(start, end, length)
    upper_bound_delta = upper_bound - trend_line
    lower_bound_delta = lower_bound - trend_line

    upper_slips_mask = (rand_deltas-upper_bound_delta) >= 0
    upper_deltas =  rand_deltas - upper_bound_delta
    rand_deltas[upper_slips_mask] = (upper_bound_delta - upper_deltas)[upper_slips_mask]

    lower_slips_mask = (lower_bound_delta-rand_deltas) >= 0
    lower_deltas =  lower_bound_delta - rand_deltas
    rand_deltas[lower_slips_mask] = (lower_bound_delta + lower_deltas)[lower_slips_mask]

    return trend_line + rand_deltas

def generateGBM(T, mu, sigma, S0, dt):
    '''
    Generate a geometric brownian motion time series. Shamelessly copy pasted from here: https://stackoverflow.com/a/13203189

    Params: 

    T: time horizon 
    mu: drift
    sigma: percentage volatility
    S0: initial price
    dt: size of time steps

    Returns: 

    t: time array
    S: time series
    '''
    N = round(T/dt)
    t = np.linspace(0, T, N)
    W = np.random.standard_normal(size = N) 
    W = np.cumsum(W)*np.sqrt(dt) ### standard brownian motion ###
    X = (mu-0.5*sigma**2)*t + sigma*W 
    S = S0*np.exp(X) ### geometric brownian motion ###
    return t, S

def generateBoundedGBM(T, sigma, start, end, dt):
    '''
    Generate a bounded geometric brownian motion making use of a brownian bridge.

    Params: 

    T: time horizon
    sigma: volatility
    start: start price
    end: end price
    dt: time steps size

    Returns: 

    t: time array
    S: time series
    '''

    S0 = start
    mu =  (1/T)*np.log(end/start) + (sigma**2)/2
    N = round(T/dt)
    t = np.linspace(0, T, N)
    W = np.random.standard_normal(size = N)
    W = np.cumsum(W)*np.sqrt(dt)
    W = W - (t/T)*W[-1]
    X = (mu-0.5*sigma**2)*t + sigma*W
    S = S0*np.exp(X)
    return t, S