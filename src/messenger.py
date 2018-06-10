import time
from termcolor import cprint
from math import floor, ceil


class Messenger(object):
    """
    Used for handling messaging functionality
    """

    def __init__(self, secrets, settings):

        self.header_str = "\nTracking {} Bittrex Markets\n"

        self.bittrex_url = "https://bittrex.com/Market/Index?MarketName={}"

        self.console_str = {
            "buy": {
                "pause": "Pause buy tracking on {} with a high RSI of {} and a 24 hour volume of {} {} for {} minutes.",
                "resume": "Resuming tracking on all {} markets.",
                "message": "Buy on {:<10}\t->\t\tRSI: {:>2}\t\t24 Hour Volume: {:>5} {}\t\tBuy Price: {:.8f}\t\tURL: {}"
            },
            "sell": {
                "pause": "Pause sell tracking on {} with a low profit margin of {}% and an RSI of {} for {} minutes.",
                "resume": "Resume sell tracking on {}.",
                "message": "Sell on {:<10}\t->\t\tRSI: {:>2}\t\tProfit Margin: {:>4}%\t\tSell Price: {:.8f}\t\tURL: {}",
                "previousMessage": ""
            }
        }

        self.error_str = {
            "market": "Failed to fetch Bittrex markets.",
            "coinMarket": "Failed to fetch Bittrex market summary for the {} market.",
            "sell": "Failed to sell on {} market. Bittrex error message: {}",
            "buy": "Failed to buy on {} market. Bittrex error message: {}",
            "order": "Failed to complete order with UUID {} within {} seconds on {} market. URL: {}",
            "balance": "Failed to fetch user Bittrex balances.",

            "SSL": "An SSL error occurred.",
            "connection": "Unable to connect to the internet.",
            "JSONDecode": "Failed to decode JSON.",
            "typeError": "Type error occurred.",
            "keyError": "Invalid key provided to obj/dict.",
            "valueError": "Value error occurred.",
            "unknown": "An unknown exception occurred.",

            "general": "See the latest log file for more information."
        }

    def print_header(self, num_of_coin_pairs):
        """
        Used to print the console header

        :param num_of_coin_pairs: Number of available Bittrex market pairs
        :type num_of_coin_pairs: int
        """
        cprint(self.header_str.format(num_of_coin_pairs), attrs=["bold", "underline"])

    def print_buy(self, coin_pair, current_buy_price, rsi, day_volume):
        """
        Used to print a buy's info to the console

        :param coin_pair: String literal for the market (ex: BTC-LTC)
        :type coin_pair: str
        :param current_buy_price: Market's current price
        :type current_buy_price: float
        :param rsi: The coin pair's RSI
        :type rsi: float
        :param day_volume: Coin pair's current 24 hour volume
        :type day_volume: float
        """
        main_market, coin = coin_pair.split("-")
        message = self.console_str["buy"]["message"].format(
            coin_pair, ceil(rsi), floor(day_volume), main_market, current_buy_price, self.get_bittrex_URL(coin_pair)
        )
        cprint(message, "blue", attrs=["bold"])

    def print_sell(self, coin_pair, current_sell_price, rsi, profit_margin):
        """
        Used to print a sales's info to the console

        :param coin_pair: String literal for the market (ex: BTC-LTC)
        :type coin_pair: str
        :param current_sell_price: Market's current price
        :type current_sell_price: float
        :param rsi: The coin pair's RSI
        :type rsi: float
        :param profit_margin: Profit made on the trade
        :type profit_margin: float
        """
        message = self.console_str["sell"]["message"].format(
            coin_pair, floor(rsi), round(profit_margin, 2), current_sell_price, self.get_bittrex_URL(coin_pair)
        )
        color = "green"
        if profit_margin <= 0:
            color = "red"
        cprint(message, color, attrs=["bold"])

    def print_pause(self, coin_pair, data, pause_time, pause_type):
        """
        Used to print coin pause info to the console

        :param coin_pair: String literal for the market (ex: BTC-LTC)
        :type coin_pair: str
        :param data: Relevant pause values
        :type data: list
        :param pause_time: The amount of minutes to tracking will be paused on the coin pair
        :type pause_time: float
        :param pause_type: Type of pause (one of: 'buy', 'sell')
        :type pause_type: str
        """
        if pause_type == "buy":
            main_market, coin = coin_pair.split("-")
            data[0] = floor(data[0])
            data[1] = floor(data[1])
            print_str = self.console_str[pause_type]["pause"].format(
                coin_pair, data[0], data[1], main_market, round(pause_time)
            )
            cprint(print_str, "yellow")
        elif pause_type == "sell":
            data[0] = round(data[0], 2)
            data[1] = floor(data[1])
            print_str = self.console_str[pause_type]["pause"].format(coin_pair, data[0], data[1], round(pause_time))
            cprint(print_str, "yellow")

    def print_no_buy(self, coin_pair, rsi, day_volume, current_buy_price):
        """
        Used to print a no-buy's info to the console

        :param coin_pair: String literal for the market (ex: BTC-LTC)
        :type coin_pair: str
        :param rsi: The coin pair's RSI
        :type rsi: float
        :param day_volume: Coin pair's current 24 hour volume
        :type day_volume: float
        :param current_buy_price: Market's current price
        :type current_buy_price: float
        """
        main_market, coin = coin_pair.split("-")
        print_str = "No " + self.console_str["buy"]["message"].format(
            coin_pair, ceil(rsi), floor(day_volume), main_market, current_buy_price, self.get_bittrex_URL(coin_pair)
        )
        cprint(print_str, "white")

    def print_no_sell(self, coin_pair, rsi, profit_margin, current_sell_price):
        """
        Used to print a no-sales's info to the console

        :param coin_pair: String literal for the market (ex: BTC-LTC)
        :type coin_pair: str
        :param rsi: The coin pair's RSI
        :type rsi: float
        :param profit_margin: Profit made on the trade
        :type profit_margin: float
        :param current_sell_price: Market's current price
        :type current_sell_price: float
        """
        print_str = "No " + self.console_str["sell"]["message"].format(
            coin_pair, floor(rsi), round(profit_margin, 2), current_sell_price, self.get_bittrex_URL(coin_pair)
        )
        if print_str != self.console_str["sell"]["previousMessage"]:
            color = "magenta"
            if profit_margin <= 0:
                color = "red"
            self.console_str["sell"]["previousMessage"] = print_str
            cprint(print_str, color)

    def print_resume_pause(self, data, pause_type):
        """
        Used to print coin pause resume info to the console

        :param data: Relevant resume value
        :type data: float
        :param pause_type: Type of pause (one of: 'buy', 'sell')
        :type pause_type: str
        """
        print_str = self.console_str[pause_type]["resume"].format(data)
        cprint(print_str, "yellow", attrs=["bold"])

    def print_error(self, error_type, data=None, will_exit=False):
        """
        Prints the error type message to the console

        :param error_type: The error type
            (one of: 'market', 'coinMarket', 'sell', 'buy', 'order', 'connection', 'SSL', 'JSONDecode', 'keyError',
            'valueError', 'typeError', 'unknown')
        :type error_type: str
        :param data: Relevant error information
        :type data: list
        :param will_exit: Whether the program is exiting or not
        :type will_exit: bool

        :return: Error string
        :rtype: str
        """
        suffix = ""
        if will_exit:
            suffix = " Exiting program."
        elif error_type in ['connection', 'SSL', 'JSONDecode', 'keyError', 'valueError', 'typeError', 'unknown']:
            suffix = " Waiting 10 seconds and then retrying."

        error_str = self.error_str[error_type]
        if error_type == "coinMarket":
            error_str = error_str.format(data[0])
        elif error_type in ["sell", "buy"]:
            error_str = error_str.format(data[0], data[1])
        elif error_type == "order":
            error_str = error_str.format(data[0], data[1], data[2], self.get_bittrex_URL(data[2]))

        cprint("\n" + error_str + suffix, "red", attrs=["bold"])
        cprint(self.error_str["general"] + "\n", "grey", attrs=["bold"])

        return error_str

    def get_bittrex_URL(self, coin_pair):
        """
        Generates the URL string for the coin pairs Bittrex page
        """
        return self.bittrex_url.format(coin_pair)
