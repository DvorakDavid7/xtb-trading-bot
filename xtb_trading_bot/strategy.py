import random
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if random.randint(1, 5) > 3:
            self.buy()
        else:
            self.sell()

if __name__ == "__main__":
    pass
    # bt = Backtest(GOOG, SmaCross, cash=10000, commission=.002, exclusive_orders=True)
    # output = bt.run()
    # print(output)
    # bt.plot(filename="plot.html")
