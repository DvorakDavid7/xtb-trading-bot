import json, logging
import queue
import random
import threading
import time
import pandas as pd

from xtb_trading_bot.commands import *
from websockets.sync.client import connect, ClientConnection
from lightweight_charts import Chart
from xtb_trading_bot.time_utils import TimeStamp


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class XtbClient():
    conn: ClientConnection
    stream_conn: ClientConnection

    def __init__(self, client_id: str, password: str, url: str, stream_url: str, data_queue: queue.Queue):
        self.client_id = client_id
        self.password = password
        self.url = url
        self.stream_url = stream_url
        self.data_queue = data_queue

        self.stream_session_id = ""

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
        self.stream_conn = connect(self.stream_url, max_size=None)
        logger.info(f"successfully connected to stream {self.stream_url}")

    def get_all_symbols(self):
        cmd = cmd_get_all_symbols()
        self._send_command(self.conn, cmd)

        filename = "symbols.json"
        message = self.conn.recv()
        with open(filename, "w") as file:
            file.write(str(message))
        logger.info(f"symbols written to the '{filename}' file")

    def get_symbol(self, symbol: str):
        cmd = cmd_get_symbol(symbol)
        self._send_command(self.conn, cmd)
        message = self.conn.recv()
        logger.info(message)

    def get_chart_last_request(self, symbol: str, start: TimeStamp, period: Period) -> pd.DataFrame:
        cmd = cmd_get_chart_last_request(symbol, start, period)
        self._send_command(self.conn, cmd)
        data = json.loads(self.conn.recv())
        # logger.info(data)

        if data["status"] != True:
            logger.error("false status, ", data)
            raise ValueError("false status")

        return_data = data["returnData"]
        digits = return_data["digits"]
        rate_infos = return_data["rateInfos"]

        table = {
            "date": [],
            "volume": [],
            "open": [],
            "close": [],
            "high": [],
            "low": []
        }

        for val in rate_infos:
            o = val["open"]
            open_ = o / (10 ** digits)
            close = (o + val["close"]) / (10 ** digits)
            high = (o + val["high"]) / (10 ** digits)
            low = (o + val["low"]) / (10 ** digits)

            volume = val["vol"]
            date = pd.to_datetime(val["ctm"], unit="ms").tz_localize("UTC").tz_convert("Europe/Prague")

            table["open"].append(open_)
            table["close"].append(close)
            table["high"].append(high)
            table["low"].append(low)
            table["date"].append(date)
            table["volume"].append(volume)
            
        return pd.DataFrame(data=table)


    def subscribe_to_get_keep_alive(self):
        cmd = cmd_get_keep_alive(self.stream_session_id)
        self._send_command(self.stream_conn, cmd)

    def subscribe_to_get_candles(self, symbol: str):
        # this must be called before reading live data
        # https://github.com/peterszombati/xapi-node/issues/17
        self.get_symbol(symbol)

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
            self.data_queue.put(message)

    def _send_command(self, connection: ClientConnection, cmd: str):
        try:
            logger.info(f"sending command: {cmd}")
            connection.send(cmd)
        except Exception as e:
            logger.error(f"ERROR: while sending command {cmd} to the socket: {e}")
            raise
