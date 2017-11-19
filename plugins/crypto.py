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

    !cryptobot symbol <coin name>: get symbol for a coin based on its name.
    """

    name = "cryptobot"

    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        self.market = Market()
        # init history object from crypto compare library
        self.history = crycompare.History()
        self.price = crycompare.Price()


    def cmd_snapshot(self, event, symbol, convert='ETH'):
        """

        :param event:
        :param symbol:
        :param convert:
        :return:
        """
        return str(json.dumps(self.price.coinSnapshot(symbol, convert), indent=4))


    def cmd_price(self, event, symbol, convert='ETH'):
        """

        :param event:
        :param symbol:
        :param convert:
        :return:
        """
        return str(self.price.price(symbol, convert))


    def cmd_symbol(self, event, name):
        """

        :param name:
        :return:
        """

        print event

        # retrieve coin list
        data = self.price.coinList()

        # get dict containing all coins
        dataDict = data['Data']

        for key in dataDict.keys():
            if dataDict[key]['CoinName'].strip().lower() == name.strip().lower():
                return key

        return 'No coin named ' + name + '.'


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


    def cmd_chartmin(self, event, symbol, from_hours, convert='ETH'):
        """

        :param event:
        :param symbol:
        :param from_hours:
        :param convert:
        :return:
        """

        # get chart data
        img_data = self._get_chart_img_data('hour', symbol, from_hours, convert)

        # upload img to server
        url = self.matrix.media_upload(img_data, 'image/png')

        return self._get_image_event_type(len(img_data), str(url['content_uri']))


    def cmd_chart(self, event, symbol, from_days, convert='ETH'):
        """

        :param event: Matrix event.
        :param symbol: Cryptocurrency symbol.
        :param from_days: Retrieves data from the past x hours.
        :return: Matrix image message.
        """

        # get chart data
        img_data = self._get_chart_img_data('days', symbol, from_days, convert)

        # upload img to server
        url = self.matrix.media_upload(img_data, 'image/png')

        return self._get_image_event_type(len(img_data), str(url['content_uri']))


    def _get_chart_img_data(self, unit, symbol, from_unit, convert):
        """

        :param unit:
        :param symbol:
        :param from_unit:
        :param convert:
        :return:
        """
        # volume color: B7C8C9
        # graph color: 1F2324
        # get timestamp
        ts = self._get_current_timestamp()

        if unit == 'days':
            data = self.history.histoHour(from_curr=symbol, to_curr=convert, limit=24 * int(from_unit), toTs=ts)
        elif unit == 'hour':
            data = self.history.histoMinute(from_curr=symbol, to_curr=convert, limit=60 * int(from_unit), toTs=ts)

        dataArr = data['Data']

        time_arr = []
        link_data = []
        volume_data = []

        for entry in dataArr:
            link_data.append(entry['close'])
            time_arr.append(datetime.datetime.fromtimestamp(entry['time']))
            volume_data.append(int(entry['volumefrom']) + int(entry['volumeto']))

        trace = graph.Scatter(
            x=time_arr,
            y=link_data,
            name=symbol + ' price last ' + str(from_unit) + ' ' + unit,
            opacity=0.5,
            marker=dict( color='1F2324' )
        )

        trace1 = graph.Bar(
            x=time_arr,
            y=volume_data,
            name=symbol + ' volume last ' + str(from_unit) + ' ' + unit,
            yaxis='y2',
            marker=dict(color='B7C8C9')
        )

        data = [ trace, trace1 ]

        layout = dict(
            title=str(symbol).upper() + ' price',
            yaxis=dict(title='Price ' + convert, overlaying='y2'),
            yaxis2=dict(title='Volume', side='right')
        )

        figure = dict(data=data, layout=layout)
        img_data = plotly.plotly.image.get(figure, width=985, height=525, scale=3)

        return img_data


    def _get_num_hours(self, weeks_ago=0, days_ago=0, hours_ago=0):
        """

        :param weeks_ago:
        :param days_ago:
        :param hours_ago:
        :return:
        """
        return weeks_ago * 7 * 24 + days_ago * 24 + hours_ago


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
        return (datetime.datetime.now() - datetime.timedelta(weeks=weeks_ago, days=days_ago, hours=hours_ago,
                                                      minutes=minutes_ago, seconds=seconds_ago)).total_seconds()


    def _get_current_timestamp(self):
        """

        :return:
        """
        return int((datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds())


    def _get_image_event_type(self, size, url, body='file.png', height=525, mime_type='image/png', width=985):
        """

        :param body:
        :param height:
        :param mime_type:
        :param size:
        :param width:
        :param url:
        :return:
        """
        body = str(self._get_current_timestamp()) + '.png'
        msg_dict = {}
        msg_dict['body'] = body
        msg_dict['info'] = {}
        msg_dict['info']['h'] = int(height)
        msg_dict['info']['mimetype'] = str(mime_type)
        msg_dict['info']['size'] = int(size)
        msg_dict['info']['w'] = int(width)
        msg_dict['msgtype'] = 'm.image'
        msg_dict['url'] = url

        return msg_dict


