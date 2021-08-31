# defisaver-sim

## What is this?

This project is intended to provide a suite of tools to simulate the behavior of automated DeFi Saver vaults.  

An example scrit is included that lets users simulate the behavior of an arbitrary vault under Geometric Brownian Motion assumptions.

``modules/cdp.py`` contains the logic of CDPs as a ``CDP()`` class. Collateral and debt can be added or removed, automation is turned off by default but can be enabled by providing some automation settings. Boost and Repay functions can be called even without automation turned on. A derivation of the formulas used for these functions will be provided in a separate document. Note: currently the implementation doesn't take into account some of the conditions used by the DeFi Saver team. In particular, there is no emergency repay if close to some liquidation threshold, and there is no conditin on the max fees charged. This is left for a later update. NOTE: because of this, it might be that if a position is too small initially, the gas fee charged when boosting or repaying would make the operation impossible. In this case, the functions will throw an error.

``modules/pricegeneration.py`` contains a collection of functions used to generate diverse price actions:

- Simple linear interpolation between some price points, assuming for example a price going from A to B where B > A with 3 corrections of 20%, 10% and 40% respectively.
- Simplified sideways price action as a sine wave.
- Bounded random walk with prescribed standard deviation.
- Geometric Brownian Motion (GBM).

``simulate_brownian.py`` is an example script using the above modules to generate a distribution of returns under GBM for some given automation settings. It is associated with a ``config.ini`` file where simulations parameters need to be set. NOTE: if the position if too small initially as discussed above, the simulation script considers the position "ruined" if it's not possible to update it with the current gas price. It is then simply closed and the amount of collateral obtained after closing is used to calculate returns.

## Requirements

Python 3.

``pip install numpy``
``pip install scipy``
``pip install matplotlib``
