import time
import json
from requests.exceptions import ConnectionError, SSLError

from messenger import Messenger
from trader import Trader
from logger import logger
from directory_utilities import get_json_from_file


def get_secrets():
    secrets_file_directory = "../database/secrets.json"
    secrets_template = {
        "bittrex": {
            "bittrexKey": "BITTREX_API_KEY",
            "bittrexSecret": "BITTREX_SECRET"
        },
    }
    secrets_content = get_json_from_file(secrets_file_directory, secrets_template)
    if secrets_content == secrets_template:
        print("Please complete the `secrets.json` file in your `database` directory")
        exit()

    return secrets_content


def get_settings():
    settings_file_directory = "../database/settings.json"
    settings_template = {
        "sound": false,
        "tradeParameters": {
            "tickerInterval": "fiveMin",
            "buy": {
                "btcAmount": 0.001,
                "rsiThreshold": 20,
                "24HourVolumeThreshold": 25,
                "minimumUnitPrice": 0.00001,
                "maxOpenTrades": 3
            },
            "sell": {
                "lossMarginThreshold": -2.5,
                "rsiThreshold": 50,
                "minProfitMarginThreshold": 0.5,
                "profitMarginThreshold": 2.5
            }
        },
        "pauseParameters": {
            "buy": {
                "rsiThreshold": 0,
                "pauseTime": 0
            },
            "sell": {
                "profitMarginThreshold": 0,
                "pauseTime": 0
            },
            "balance": {
                "pauseTime": 0
            }
        }
    }

    settings_content = get_json_from_file(settings_file_directory, settings_template)
    if settings_content == settings_template:
        print("Please complete the `settings.json` file in your `database` directory")
        exit()

    return settings_content


if __name__ == "__main__":
    secrets = get_secrets()
    settings = get_settings()

    Messenger = Messenger(secrets, settings)
    Trader = Trader(secrets, settings)

    Trader.initialise()

    while True:
        try:
            Trader.analyse_pauses()
            Trader.analyse_buys()
            Trader.analyse_sells()
            time.sleep(10)

        except SSLError as exception:
            Messenger.print_error("SSL")
            logger.exception(exception)
            time.sleep(10)
        except ConnectionError as exception:
            Messenger.print_error("connection")
            logger.exception(exception)
            time.sleep(10)
        except json.decoder.JSONDecodeError as exception:
            Messenger.print_error("JSONDecode")
            logger.exception(exception)
            time.sleep(10)
        except TypeError as exception:
            Messenger.print_error("typeError")
            logger.exception(exception)
            time.sleep(10)
        except KeyError as exception:
            Messenger.print_error("keyError", [], True)
            logger.exception(exception)
            exit()
        except ValueError as exception:
            Messenger.print_error("valueError", [], True)
            logger.exception(exception)
            exit()
        except Exception:
            Messenger.print_error("unknown", [], True)
            logger.exception(Exception)
            exit()
