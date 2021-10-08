# defisaver-sim

## What is this?

This project is intended to provide a suite of tools to simulate the behavior of automated DeFi Saver vaults.  

Example scripts are included to let users simulate or optimize automated vaults under specific conditions.

## Requirements

Python 3.

``pip install numpy``
``pip install scipy``
``pip install matplotlib``

## Project structure

``modules/cdp.py`` contains the logic of CDPs as a ``CDP()`` class. Collateral and debt can be added or removed, automation is turned off by default but can be enabled by providing some automation settings. Boost and Repay functions can be called even without automation turned on. A derivation of the formulas used for these functions will be provided in a separate document. Note: currently the implementation doesn't take into account some of the conditions used by the DeFi Saver team. In particular, there is no emergency repay if close to some liquidation threshold, and there is no conditin on the max fees charged. This is left for a later update. NOTE: because of this, it might be that if a position is too small initially, the gas fee charged when boosting or repaying would make the operation impossible. In this case, the functions will throw an error.

``modules/pricegeneration.py`` contains a collection of functions used to generate diverse price actions:

- Simple linear interpolation between some price points, assuming for example a price going from A to B where B > A with 3 corrections of 20%, 10% and 40% respectively.
- Simplified sideways price action as a sine wave.
- Bounded random walk with prescribed standard deviation.
- Geometric Brownian Motion (GBM).
- Geometric Brownian Motion with prescribed start and end points.

``modules/simulate.py`` contains all the functions used to run actual simulations of automated vaults, including simulations of a collection of sample paths.

``modules/optimize.py`` contains functions used to find optimal parameters for constant leverage or leveraged automated vault strategies.

``simulate_brownian.py`` is an example script using the above modules to generate a distribution of returns under GBM for some given automation settings. It is associated with a ``config.ini`` file where simulations parameters need to be set. NOTE: if the position if too small initially as discussed above, the simulation script considers the position "ruined" if it's not possible to update it with the current gas price. It is then simply closed and the amount of collateral obtained after closing is used to calculate returns.

## How to use for simple simulations?

This section is for non-technical users who would like to make practical use of this project.

If you would just like to use this project for simple simulations of your own positions, or optimize the settings of one of your positions, you just need to enter your parameters in the ``config.ini`` file (open with a text editor), and then run one of the scripts in the top level folder

The ``config.ini`` should contained all the comments necessary to understand what changes to make.

Once you have filled the section corresponding to what you are trying to simulate / optimize, open the command line and navigate to the repo. For example if your username is ``user`` and you cloned the repo in ``Documents``, open the command line and type ``cd C:\Users\user\Documents\defisaver-sim``.  Then run the following commands depending on what you're doing:

- For simulations of a collection of random paths with prescribed drift, but no fixed endpoint, run ``python simulate_brownian.py``.

- For simulations of a collection of random paths with fixed start and end points, run ``python simulate_bounded_brownian.py``.

- For finding the optimal leverage ratio in the theoretical case of perfectly continuous constant leverage, run ``python continuous_optimization_script.py``.

- For finding the optimal automation parameters of a leveraged vault on DeFi Saver, run ``python automated_vault_optimization_script.py``. WARNING: this can take a while to run.
