from neb.plugins import Plugin
from coinmarketcap import Market
import crycompare

import json

class CryptoPlugin(Plugin):
    """
    Crypto bot for matrix.
    """

    name = "cryptobot"

    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        self.market = Market()

    def cmd_cap(self, event, id, convert='ETH'):
        """

        :param event:
        :param id:
        :return:
        """
        ticker_data = self.market.ticker(id, convert=convert)
        return str(json.dumps(ticker_data, sort_keys=True, indent=4))

    def cmd_stats(self, event, convert='USD'):
        """

        :param event:
        :return:
        """
        stats_data = self.market.stats(convert=convert)
        return str(json.dumps(stats_data, sort_keys=True, indent=4))