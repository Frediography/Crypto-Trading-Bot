# Crypto Trading Bot

Taken from https://github.com/JPStrydom/Crypto-Trading-Bot - this is just my version of the bot, taking out some features I didn't want and trialling a few that I did...

#### Shoutouts:
* Bittrex for an awesome API
* Eric Somdahl for writing the Python wrapper for the Bittrex API
* Abenezer Mamo for creating the [Crypto Signals](https://github.com/AbenezerMamo/crypto-signal) project which formed the
foundation for this project
* JPStrydom for writing the bot before I started to hack away at it!!!

## How to setup
1) This project requires Python 3.X.X, which can be be found [here](https://www.python.org/ftp/python/3.6.3/python-3.6.3.exe).

2) To install the dependencies for this project, run one of the following commands:
    * Windows: `pip3 install -r requirements.txt`

        *NOTE: If you receive a `'pip3' is not recognized as an internal or external command` error, you
        need to add `pip3` to your environmental `path` variable.*

    * Unix: `sudo pip3 install -r requirements.txt`

3) Add a directory named `database` to the root directory of your project and add a `secrets.json` file to it. If you
run the project without adding this file, the program will create it for you and populate it with the template values.

    1) To use the **Bittrex** functionality, you need to setup the following:
        * **`bittrex_key`** is your Bittrex API key you can get from [here](https://bittrex.com/Manage#sectionApi)
        * **`bittrex_secret`** is your Bittrex API secret key

        *NOTE: The `READ INFO`, `TRADE LIMIT`, and `TRADE MARKET` permissions need to be enabled on your API key in
        order for the trade functionality to be available*

4) Add a `settings.json` file to the newly created `database` directory. If you run the project without adding this file,
the program will create it for you and populate it with the template values.

    2) To use the **Trade** functionality, you need to setup the following:
        * **`tickerInterval`** is the exchange ticker interval you want to use. It should be one of the following: `oneMin`,
        `fiveMin`, `thirtyMin`, `hour`, `week`, `day`, `month`
        * **`buy`**:
            * `btcAmount` is the amount of BTC you want the bot to spend per buy
            * `rsiThreshold` is the upper RSI buy threshold. An RSI lower than this will result in a buy signal
            * `24HourVolumeThreshold` is the lower 24 hour volume buy threshold. Coin pairs with a 24 hour volume lower than
            this will not be considered for buying
            * `minimumUnitPrice` is the lower unit price buy threshold. Coin pairs with a unit price lower than this will not
            be considered for buying
            * `maxOpenTrades` is the maximum amount of open trades the bot is allowed to have at one time
        * **`sell`**:
            * `lossMarginThreshold` is the lower loss margin threshold. Coin pairs with a profit margin lower than this
            will be sold if their RSI is above the `sell` `rsiThreshold`. If this value is omitted or set to zero (`0`),
            this parameter will be ignored and coin pairs will not be sold at a loss
            * `rsiThreshold` is the lower RSI sell threshold. An RSI higher than this will result in a sell signal
            * `minProfitMarginThreshold` is the upper minimum profit margin sell threshold. Coin pairs with a profit margin
            lower than this will not be sold
            * `profitMarginThreshold` is the upper profit margin sell threshold. Coin pairs with a profit margin higher than
            this will be sold regardless of its RSI

    3) To use the **Pause** functionality, you need to setup the following:
        * **`buy`**:
            * `rsiThreshold` is the lower RSI pause threshold. An RSI higher than this will result in the coin pair not being
            tracked for `pauseTime` minutes
            * `pauseTime` is the amount of minutes to pause coin pair tracking by
        * **`sell`**:
            * `profitMarginThreshold` is the upper profit margin pause threshold. A profit margin lower than this will result
            in the coin pair not being tracked for `pauseTime` minutes
            * `pauseTime` is the amount of minutes to pause coin pair tracking by
            If you prefer to sell at a small loss rather than holding onto (pausing) sell coin pairs, the `lossMarginThreshold`
            **trade** parameter should be set appropriately and then the `sell` **pause** parameter may be omitted.
        * **`balance`**:
            * `pauseTime` is the amount of minutes you would like to wait in between balance notification Slack messages
            (i.e. every *x* minutes, you will receive a Slack message containing a breakdown of your exchange balance
            and the percentage change since your last balance notification message).


## How to run
Navigate to the `src` file directory in terminal, and run the command `python app.py` to start the trading bot.

## Trading
This system allows you to autonomously make and track crypto currency trades on Bittrex. It uses a local database strategy to ensure data is not lost.

To use this functionality, first set the desired trade parameters in the `settings.json` file.

The `analyse_buys()` and `analyse_sells()` functions will then apply the `buy_strategy(coin_pair)` and
`sell_strategy(coin_pair)` functions to each valid coin pair on Bittrex. These functions will check each coin pair for
buy/sell signals by utilising the the following two functions:
```python
from directory_utilities import get_json_from_file

settings_file_directory = "../database/settings.json"
settings = get_json_from_file(settings_file_directory)

buy_trade_params = settings["tradeParameters"]["buy"]
sell_trade_params = settings["tradeParameters"]["sell"]

def check_buy_parameters(rsi, day_volume, current_buy_price):
    """
    Used to check if the buy conditions have been met

    :param rsi: The coin pair's current RSI
    :type rsi: float
    :param day_volume: The coin pair's current 24 hour volume
    :type day_volume: float
    :param current_buy_price: The coin pair's current price
    :type current_buy_price: float

    :return: Boolean indicating if the buy conditions have been met
    :rtype: bool
    """
    rsi_check = rsi is not None and rsi <= buy_trade_params["buy"]["rsiThreshold"]
    day_volume_check = day_volume >= buy_trade_params["buy"]["24HourVolumeThreshold"]
    current_buy_price_check = current_buy_price >= buy_trade_params["buy"]["minimumUnitPrice"]

    return rsi_check and day_volume_check and current_buy_price_check


def check_sell_parameters(rsi, profit_margin):
    """
    Used to check if the sell conditions have been met

    :param rsi: The coin pair's current RSI
    :type rsi: float
    :param profit_margin: The coin pair's current profit margin
    :type profit_margin: float

    :return: Boolean indicating if the sell conditions have been met
    :rtype: bool
    """
    rsi_check = rsi is not None and rsi >= sell_trade_params["sell"]["rsiThreshold"]
    lower_profit_check = profit_margin >= sell_trade_params["sell"]["minProfitMarginThreshold"]        
    upper_profit_check = profit_margin >= sell_trade_params["sell"]["profitMarginThreshold"]
    loss_check = (sell_trade_params["lossMarginThreshold"] is not None and
                  0 > sell_trade_params["lossMarginThreshold"] >= profit_margin)

    return (rsi_check and lower_profit_check) or upper_profit_check or loss_check
```

See the source code for a more detailed description.

## Disclaimer
- Do not use this code
- I am playing with it as a toy only, not to make money
- Do not try to make money with it
- Do not use it with real money unless you have changed it to the point it works - which it doesn't right now.
