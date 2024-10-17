import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

from xtb_trading_bot.commands import Period
from xtb_trading_bot.time_utils import TimeStamp
from xtb_trading_bot.xtb_client import XtbClient


class SmaCross(Strategy):
    n1 = 5
    n2 = 15

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        print(self.position.pl)
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


if __name__ == "__main__":
    client = XtbClient()
    client.login()
    symbol = "ETHEREUM"
    df = client.get_chart_last_request(symbol, TimeStamp().now().sub_hr(10), Period.PERIOD_M1)

    bt = Backtest(df, SmaCross, cash=3000)

    result = bt.run()

    bt.plot(filename="plot.html")

    print(result)

    # stats = bt.optimize(n1=range(5, 30, 5),
    #                     n2=range(10, 70, 5),
    #                     maximize='Equity Final [$]',
    #                     constraint=lambda param: param.n1 < param.n2)
    # print(stats._strategy)

    # print(result)
