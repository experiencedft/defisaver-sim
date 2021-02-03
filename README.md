# defisaver-sim

## What is this?

This project is intended to provide a suite of tools to simulate the behavior of automated DeFi Saver vaults.  

An example scrit is included that lets users simulate the behavior of an arbitrary vault under simplified price action profiles: uptrend, downtrend, or sideways.

**Uptrend:** Final price higher than the initial price, with the possibility of a user-specified number of corrections with given amplitudes in % of the current price along the way. The price is allowed to go below the initial price if one of the corrections is too steep. Simple linear interpolation between local extrema.

**Downtrend:** Final price lower than the initial price, with the possibility of a user-specified number of bounces with given amplitudes in % of the current price along the way. The price is allowed to go above the initial price if one of the corrections is too steep. Simple linear interpolation between local extrema.

**Sideways:** The user chooses an average price. The price then oscillates in a sinusoid around that average price with a given amplitude in % of the initial price for a given number of cycles. One cycle is defined as the price starting from the average, going up by X%, back to the average, and down by X%, where X is the user-specified amplitude.

The boost and repay functions are agnostic and can be used with any vault (Python dictionary) at any price (float).

## How to use?

1. Clone the repo.

2. Install Python 3 with your distribution of choice.

3. If they are not part of your distribution, install numpy and matplotlib from the command line by running ``pip install numpy`` and ``pip install matplotlib``.

4. Navigate to the folder in the command line and run ``python cmd_vault_simulation.py``.

5. Follow the instructions displayed to run your simulation.
