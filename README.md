# defisaver-sim

## What is this?

Use this script to simulate the behavior of your automated Maker vault under different market conditions.

Currently only let's the user create simplified price action profiles: uptrend, downtrend or sideways.

Uptrend: Final price higher than the initial price, with the possibility of a user specified number of corrections with given amplitudes in % of the current price along the way. The price is allowed to go below the initial price if one of the corrections is too steep. Simple linear interpolation between local extrema.

Downtrend: Final price lower than the initial price, with the possibility of a user specified number of bounces with given amplitudes in % of the current price along the way. The price is allowed to go above  the initial price if one of the corrections is too steep. Simple linear interpolation between local extrema.

Sideways: The user chooses an average price. The price then oscillates in a sinusoid around that average price with a given amplitude in % of the initial price for a given number of cycles. One cycle hear is defined as the price starting from the average, going up by X%, back to the average, and down by X%, where X is the user specified amplitude.

The boost and repay functions are agnostic and can be used with any vault (Python dictionary) at any price (float).

## How to use?

Clone the repo, navigate in the folder in the command line, run ``python simulation.py``, and follow the instructions.
