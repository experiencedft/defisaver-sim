'''
Run several simulations of an automated leveraged vault under a geometric brownian 
motion with prescribed volatility and drift and average the returns.
'''

from modules.readConfig import readConfig

from scipy import stats
from scipy.integrate import quad
import numpy as np 
import matplotlib.pyplot as plt

from modules import cdp
from modules import pricegeneration as pr

init_portfolio, init_collateralization, repay_from, repay_to, boost_from, boost_to, service_fee, gas_price, N_paths, volatility, drift, init_price, time_horizon, time_step_size = readConfig("Brownian simulation parameters")

# Terminal returns denominated in collateral asset and debt asset 
# for each price path, expressed in multiplier
returns_col = []
returns_debt = []

# The maximum loss in debt asset recorded for each price path, in %
max_loss_debt = []

for i in range(N_paths): 
    vault = cdp.CDP(0, 0, 0)
    vault.changeCollateral(init_portfolio)
    vault.boostTo(init_collateralization, init_price, gas_price, service_fee)
    vault.automate(repay_from, repay_to, boost_from, boost_to)
    #Portfolio value in collateral asset and debt asset respectively
    V_col = [init_portfolio]
    V_debt = [init_portfolio*init_price]
    t, path = pr.generateGBM(1, drift, volatility, init_price, time_step_size)
    for price in path:
        if vault.getCollateralizationRatio(price) > vault.automation_settings["boost from"]:
            _ = vault.boostTo(vault.automation_settings["boost to"], price, gas_price, service_fee)
            if _ == "Ruined": 
                V_col.append(vault.close(price))
                V_debt.append(path[-1]*vault.close(price))
                break
        elif vault.getCollateralizationRatio(price) < vault.automation_settings["repay from"]:
            _ = vault.repayTo(vault.automation_settings["repay to"], price, gas_price, service_fee)
            if _ == "Ruined":
                V_col.append(vault.close(price))
                V_debt.append(path[-1]*vault.close(price))
                break
        V_col.append(vault.collateral - vault.debt/price)
        V_debt.append(price*(vault.collateral - vault.debt/price))
    # In %
    # returns_col.append(100*(V_col[-1]/V_col[0] - 1))
    # returns_debt.append(100*(V_debt[-1]/V_debt[0] - 1))
    # In multiplier
    max_loss_debt.append(100*(1- min(V_debt)/max(V_debt)))
    returns_col.append(V_col[-1]/V_col[0])
    returns_debt.append(V_debt[-1]/V_debt[0])
    # print(returns_debt)

print("Minimum overall return: ", round(min(returns_debt), 2),"X")
print("Maximum overall return: ", round(max(returns_debt), 2), "X")
print("Max transient loss: ", round(max(max_loss_debt), 3), "%")

returns_debt = np.array(returns_debt)
returns_col = np.array(returns_col)
log_returns_debt = np.log(returns_debt)
log_returns_col = np.log(returns_col)

m, s = stats.norm.fit(log_returns_debt)

plt.figure(figsize = [9, 6.5])

binwidth = abs((max(log_returns_debt) - min(log_returns_debt))/(N_paths/10))
plt.hist(log_returns_debt, np.arange(min(log_returns_debt), max(log_returns_debt) + binwidth, binwidth), density=True)

xt = plt.xticks()[0]
xmin, xmax = min(xt), max(xt)
x = np.linspace(xmin, xmax, len(log_returns_debt))
def pdf_fit(x):
    return stats.norm.pdf(x, m, s)

print("Probability of profit: ", round(100*quad(pdf_fit, 0, xmax)[0], 2), "%")
print("Probability of outperforming: ", round(100*quad(pdf_fit, drift, 2*xmax)[0],2), "%")
print("Probability of outperforming by a factor of 10: ", round(100*quad(pdf_fit, drift+np.log(10), 2*xmax)[0]), "%")
print("Probability of outperforming by a factor of 50: ", round(100*quad(pdf_fit, drift+np.log(50), 2*xmax)[0]), "%")



plt.plot(x, pdf_fit(x), label=r"Gaussian fit, $\mu = {mu}$, $\sigma = {sigma}$".format(mu=round(m, 2), sigma=round(s, 2)))
plt.title("Distribution of log-returns for a TCL strategy \n" + 
r"$R_f = {rf}, \ R_t = {rt}$".format(rf = repay_from, rt = repay_to) + " | "
r"$B_f = {bf}, \ B_t = {bt}$".format(bf = boost_from, bt = boost_to) + 
"\n" + "Market conditions (GBM): " + 
r"$\sigma_{{vol}} = {sigma},  \ \mu_{{drift}} = {mu}, \ dt = 4 \ \mathrm{{hour}}$".format(sigma = volatility, mu = drift))
plt.annotate('*Threshold-based Constant Leverage', (0.5, -0.08), (0, 0), xycoords='axes fraction', textcoords='offset points', va='top')
plt.xlim(xmin, xmax)
# plt.xlabel("Log-returns")
plt.ylabel("Probability density")
plt.legend(loc="best")
plt.tight_layout()
plt.show()