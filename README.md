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

``modules/cdp.py`` contains the logic of CDPs as a ``CDP()`` class. Collateral and debt can be added or removed, automation is turned off by default but can be enabled by providing some automation settings. Boost and Repay functions can be called even without automation turned on. A derivation of the formulas used for these functions will be provided in a separate document. 

``modules/pricegeneration.py`` contains a collection of functions used to generate diverse price actions:

- Simple linear interpolation between some price points, assuming for example a price going from A to B where B > A with 3 corrections of 20%, 10% and 40% respectively.
- Simplified sideways price action as a sine wave.
- Bounded random walk with prescribed standard deviation.
- Geometric Brownian Motion (GBM).
- Geometric Brownian Motion with prescribed start and end points.

``modules/simulate.py`` contains all the functions used to run actual simulations of automated vaults, including simulations of a collection of sample paths. At the moment, if a position can't be rebalanced anymore because of some fee condition, it is closed to the collateral asset, which is then held until the end of the simulation.

``modules/optimize.py`` contains functions used to find optimal parameters for constant leverage or leveraged automated vault strategies.

The top level folder contains a collection of scripts that may be used in tandem with parameters specified in the `config.ini` file.

## How to use for simple simulations?

This section is for non-technical users who would like to make practical use of this project.

If you would just like to use this project for simple simulations of your own positions, or optimize the settings of one of your positions, you just need to enter your parameters in the ``config.ini`` file (open with a text editor), and then run one of the scripts in the top level folder

The ``config.ini`` should contained all the comments necessary to understand what changes to make.

Once you have filled the section corresponding to what you are trying to simulate / optimize, open the command line and navigate to the repo. For example if your username is ``user`` and you cloned the repo in ``Documents``, open the command line and type ``cd C:\Users\user\Documents\defisaver-sim``.  Then run the following commands depending on what you're doing:

- For simulations of a collection of random paths with prescribed drift, but no fixed endpoint, run ``python simulate_brownian.py``.

- For simulations of a collection of random paths with fixed start and end points, run ``python simulate_bounded_brownian.py``.

- For finding the optimal leverage ratio in the theoretical case of perfectly continuous constant leverage, run ``python continuous_optimization_script.py``.

- For finding the optimal automation parameters of a leveraged vault on DeFi Saver, run ``python automated_vault_optimization_script.py``. WARNING: this can take a while to run.
