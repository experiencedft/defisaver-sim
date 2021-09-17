from configparser import ConfigParser

def readConfig(section: str):
    '''
    Read the desired section of the config file and return an array containing 
    all of the read parameters as a tuple.

    Params: 

    section: str
        the section of the config file to read
    
    Returns: 

    config: tuple

        If brownian simulation section:

        init_portfolio, init_collateralization, repay_from, repay_to, boost_from, 
        boost_to, service_fee, gas_price, N_paths, volatility, drift, init_price, 
        time_horizon, time_step_size

        If continuous limit optimization: 

        underlying_return, time_period, volatility
    '''

    #Import config 
    config_object = ConfigParser()
    config_object.read("config.ini")
    
    if section == "Brownian simulation parameters":

        # Initial value of portfolio in ETH
        init_portfolio = float(config_object.get("Brownian simulation parameters", "INITIAL_PORTFOLIO"))

        # Initial collateralization ratio
        init_collateralization = float(config_object.get("Brownian simulation parameters", "INITIAL_COLLATERALIZATION"))

        # Automation settings
        repay_from = float(config_object.get("Brownian simulation parameters", "REPAY_FROM"))
        repay_to = float(config_object.get("Brownian simulation parameters", "REPAY_TO"))
        boost_from = float(config_object.get("Brownian simulation parameters", "BOOST_FROM"))
        boost_to = float(config_object.get("Brownian simulation parameters", "BOOST_TO"))
        service_fee = float(config_object.get("Brownian simulation parameters", "SERVICE_FEE"))
        gas_price = float(config_object.get("Brownian simulation parameters", "GAS_PRICE"))

        # Simulation parameters

        # Number of price paths to average over
        N_paths = int(config_object.get("Brownian simulation parameters", "N_PATHS"))
        # Annualized volatility and drift of each path
        volatility = float(config_object.get("Brownian simulation parameters", "VOLATILITY"))
        drift = float(config_object.get("Brownian simulation parameters", "DRIFT")) 
        # Initial price of collateral denominated in debt asset
        init_price = float(config_object.get("Brownian simulation parameters", "INITIAL_PRICE"))
        # Time step size (in years)
        time_horizon = float(config_object.get("Brownian simulation parameters", "TIME_HORIZON"))
        time_step_size = float(config_object.get("Brownian simulation parameters", "TIME_STEP_SIZE")) 
        
        return init_portfolio, init_collateralization, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, N_paths, volatility, drift, init_price, time_horizon, time_step_size

    elif section == "Continuous limit optimization parameters":
        
        underlying_return = float(config_object.get("Continuous limit optimization parameters", "UNDERLYING_RETURN"))
        #In units of years
        time_period = float(config_object.get("Continuous limit optimization parameters", "TIME_PERIOD"))
        #In units of volatility
        volatility = float(config_object.get("Continuous limit optimization parameters", "VOLATILITY"))

        return underlying_return, time_period, volatility