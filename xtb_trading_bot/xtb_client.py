import json, logging
import random
import threading
import time

import websockets
from xtb_trading_bot.commands import cmd_get_all_symbols, cmd_get_balance, cmd_get_candles, cmd_get_chart_last_request, cmd_get_keep_alive, cmd_get_symbol, cmd_get_tick_prices, cmd_get_trades, cmd_login, cmd_ping
from websockets.sync.client import connect, ClientConnection


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

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

    def get_chart_last_request(self, symbol: str):
        cmd = cmd_get_chart_last_request(symbol)
        self._send_command(self.conn, cmd)
        message = self.conn.recv()
        logger.info(message)

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
