import json, logging
import os
import random
import threading
import time
import pandas as pd
import mplfinance as mpf


from xtb_trading_bot.commands import Period, cmd_get_all_symbols, cmd_get_balance, cmd_get_candles, cmd_get_chart_last_request, cmd_get_keep_alive, cmd_get_symbol, cmd_get_tick_prices, cmd_get_trades, cmd_login, cmd_ping
from websockets.sync.client import connect, ClientConnection

from xtb_trading_bot.time_utils import TimeStamp


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

binance_dark = {
    "base_mpl_style": "dark_background",
    "marketcolors": {
        "candle": {"up": "#3dc985", "down": "#ef4f60"},  
        "edge": {"up": "#3dc985", "down": "#ef4f60"},  
        "wick": {"up": "#3dc985", "down": "#ef4f60"},  
        "ohlc": {"up": "green", "down": "red"},
        "volume": {"up": "#247252", "down": "#82333f"},  
        "vcedge": {"up": "green", "down": "red"},  
        "vcdopcod": False,
        "alpha": 1,
    },
    "mavcolors": ("#ad7739", "#a63ab2", "#62b8ba"),
    "facecolor": "#1b1f24",
    "gridcolor": "#2c2e31",
    "gridstyle": "--",
    "y_on_right": True,
    "rc": {
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.edgecolor": "#474d56",
        "axes.titlecolor": "red",
        "figure.facecolor": "#161a1e",
        "figure.titlesize": "x-large",
        "figure.titleweight": "semibold",
    },
    "base_mpf_style": "binance-dark",
}

class XtbClient():

    conn: ClientConnection
    stream_conn: ClientConnection

    def __init__(self, client_id: str, password: str, url: str, stream_url: str):
        self.client_id = client_id
        self.password = password
        self.url = url
        self.stream_url = stream_url

        self.conn = None
        self.stream_conn = None

        self.stream_session_id = None

    def login(self):
        self.conn = connect(self.url, max_size=None)
        cmd = cmd_login(self.client_id, self.password)
        self._send_command(self.conn, cmd)

        message = json.loads(self.conn.recv())

        if message["status"] != True:
            raise ValueError(f"ERROR: invalid login: {message}")

        logger.info(f"successfully connected to {self.url}")
        self.stream_session_id = message["streamSessionId"]

    def streaming_connect(self):
        self.stream_conn = connect(self.stream_url)
        logger.info(f"successfully connected to stream {self.stream_url}")

    def get_all_symbols(self):
        cmd = cmd_get_all_symbols()
        self._send_command(self.conn, cmd)

        filename = "symbols.json"
        message = self.conn.recv()
        with open(filename, "w") as file:
            file.write(message)
        logger.info(f"symbols written to the '{filename}' file")

    def get_symbol(self, symbol: str):
        cmd = cmd_get_symbol(symbol)
        self._send_command(self.conn, cmd)
        message = self.conn.recv()
        logger.info(message)

    def get_chart_last_request(self, symbol: str, start: TimeStamp, period: Period):
        cmd = cmd_get_chart_last_request(symbol, start, period)
        self._send_command(self.conn, cmd)
        data = json.loads(self.conn.recv())
        logger.info(data)

        if data["status"] != True:
            logger.error("false status, ", data)
            raise ValueError("false status")

        return_data = data["returnData"]

        digits = return_data["digits"]
        logger.info(digits)
        rate_infos = return_data["rateInfos"]

        table = {
            "date": [],
            "volume": [],
            "open": [],
            "close": [],
            "high": [],
            "low": []
        }

        file = open("test.csv", "w")

        file.write("date, open, close, high, low, volume\n")
        for val in rate_infos:
            o = val["open"]
            open_ = o / (10 ** digits)
            close = (o + val["close"]) / (10 ** digits)
            high = (o + val["high"]) / (10 ** digits)
            low = (o + val["low"]) / (10 ** digits)

            volume = val["vol"]
            ctm_str = val["ctmString"]
            ctm = val["ctm"]

            table["open"].append(open_)
            table["close"].append(close)
            table["high"].append(high)
            table["low"].append(low)
            table["date"].append(pd.to_datetime(ctm, unit="ms").tz_localize("UTC").tz_convert("Europe/Prague"))
            table["volume"].append(volume)
            
            file.write(f"{ctm},{open_},{close},{high},{low},{volume}\n")

        df = pd.DataFrame(table)
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        df.resample("H")
        df_hourly = df.resample('H').agg({
            "open": "first",  # Open is the first price of the hour
            "high": "max",    # High is the maximum price of the hour
            "low": "min",     # Low is the minimum price of the hour
            "close": "last",  # Close is the last price of the hour
            "volume": "sum"   # Volume is the sum of the volume for the hour
        })

        print(df)
        mpf.plot(df, type="candle", style=binance_dark, volume=True)
        file.close()


    def subscribe_to_get_keep_alive(self):
        cmd = cmd_get_keep_alive(self.stream_session_id)
        self._send_command(self.stream_conn, cmd)

    def subscribe_to_get_candles(self, symbol: str):
        cmd = cmd_get_candles(self.stream_session_id, symbol)
        self._send_command(self.stream_conn, cmd)

    def subscribe_to_get_trades(self):
        cmd = cmd_get_trades(self.stream_session_id)
        self._send_command(self.stream_conn, cmd)

    def subscribe_to_get_balance(self):
        cmd = cmd_get_balance(self.stream_session_id)
        self._send_command(self.stream_conn, cmd)

    def subscribe_to_get_tick_prices(self, symbol: str):
        cmd = cmd_get_tick_prices(self.stream_session_id, symbol)
        self._send_command(self.stream_conn, cmd)

    def keep_alive(self):
        def run(ws: ClientConnection):
            while True:
                cmd = cmd_ping()
                logger.info(f"base: {cmd}")
                ws.send(cmd)
                time.sleep(10 + random.random())
        threading.Thread(target=run, args=(self.conn,), daemon=True).start()

    def read_stream(self):
        while True:
            message = self.stream_conn.recv()
            logger.info(message)

    def _send_command(self, connection: ClientConnection, cmd: str):
        try:
            logger.info(f"sending command: {cmd}")
            connection.send(cmd)
        except Exception as e:
            logger.error(f"ERROR: while sending command {cmd} to the socket: {e}")
            raise
