from neb.plugins import Plugin
from coinmarketcap import Market
import crycompare
import plotly
import plotly.graph_objs as graph
import datetime

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
        :param convert:
        :return:
        """
        stats_data = self.market.stats(convert=convert)
        return str(json.dumps(stats_data, sort_keys=True, indent=4))

    def cmd_chart(self, event, symbol, from_days, convert):
        """

        :param event:
        :param symbol:
        :param from_days:
        :return:
        """

        #get timestamp
        mtimestamp = self._get_timestamp(days_ago=from_days)

        # init history object from crypto compare library
        history = crycompare.History()

        histoDayData = history.histoHour(from_curr=symbol, to_curr=convert, )

        # histoDayData

        time_arr = []
        price_arr_high = []
        price_arr_low = []

        dataArr = histoDayData['Data']

        for n in range(len(dataArr)):
            time_arr.append(datetime.datetime.fromtimestamp(dataArr[n]['time']))
            price_arr_high.append(dataArr[n]['high'])
            price_arr_low.append(dataArr[n]['low'])

        trace_high = graph.Scatter(
            x=time_arr,
            y=price_arr_high,
            name='ETH High'
        )

        trace_low = graph.Scatter(
            x=time_arr,
            y=price_arr_low,
            name='ETH Low'
        )

        data = [trace_high, trace_low]

        layout = dict(
            title='Eth poloniex price',
            yaxis=dict(title='Price $USD')
        )

        figure = dict(data=data, layout=layout)

    def _get_timestamp(self, weeks_ago=0, days_ago=0, hours_ago=0, minutes_ago=0, seconds_ago=0):
        """

        :param months_ago:
        :param years_ago:
        :param days_ago:
        :param hours_ago:
        :param minutes_ago:
        :param seconds_ago:
        :return:
        """
        return (datetime.utcnow() - datetime.timedelta(weeks=weeks_ago, days=days_ago, hours=hours_ago,
                                                      minutes=minutes_ago, seconds=seconds_ago)).total_seconds()


