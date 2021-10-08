from modules.readConfig import readConfig
from modules.optimize import optimizeAutomationBoundedGBM

init_portfolio, min_ratio, service_fee, gas_price, volatility, start_price, end_price, time_horizon = readConfig("Automated vault optimization")
optimal_settings, optimal_expected_return, optimal_returns_debt = optimizeAutomationBoundedGBM(init_portfolio, min_ratio, service_fee, gas_price, volatility, start_price, end_price, time_horizon)
print('Optimal settings: ', optimal_settings)
print('Optimal expected return in collateral: ', optimal_expected_return)
print('Optimal expected return in debt asset: ', optimal_returns_debt)