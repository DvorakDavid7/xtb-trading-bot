import json
import queue
import pandas as pd
from threading import Thread

from lightweight_charts import Chart

class ChartingThread(Thread):
    data_queue: queue.Queue


    def __init__(self, chart: Chart, data_queue: queue.Queue):
        Thread.__init__(self)
        self.data_queue = data_queue
        self.chart = chart


    def run(self):
        while True:
            data = self.data_queue.get()
            command_json = json.loads(data)
            print(command_json)

            if command_json["command"] == "candle":
                self.handle_candle_data(command_json["data"])
            elif command_json["command"] == "tickPrices":
                # self.handle_tick_prices(command_json["data"])
                pass


    def handle_candle_data(self, candle_data: dict):
        date = pd.to_datetime(candle_data["ctm"], unit="ms").tz_localize("UTC").tz_convert("Europe/Prague")
        d = {
            "date": date,
            "volume": candle_data["vol"],
            "open": candle_data["open"],
            "close": candle_data["close"],
            "high": candle_data["high"],
            "low": candle_data["low"]
        }
        ser = pd.Series(data=d, index=list(d.keys()))
        self.chart.update(ser)

    def handle_tick_prices(self, tick_data: dict):
        date = pd.to_datetime(tick_data["timestamp"], unit="ms").tz_localize("UTC").tz_convert("Europe/Prague")
        d = {
            "date": date,
            # "volume": tick_data["askVolume"],
            "price": (tick_data["bid"] + tick_data["ask"]) / 2,
        }
        ser = pd.Series(data=d, index=list(d.keys()))
        self.chart.update_from_tick(ser)
