import threading
import time
import websocket, json, os
from typing import Any, Callable

from websocket import create_connection
from dotenv import load_dotenv

from xtb_trading_bot.commands import Period
from xtb_trading_bot.time_utils import TimeStamp
from xtb_trading_bot.xtb_client import XtbClient

load_dotenv()


SESSION_ID = ""

client_id = os.getenv("USER_ID")
password = os.getenv("PASSWORD")


login_cmd = {
	"command": "login",
	"arguments": {
		"userId": client_id,
		"password": password,
		"appId": "",
		"appName": ""
	}
}

get_ballance_cmd = {
	"command": "getBalance",
	"streamSessionId": ""
}


get_tick_price = {
	"command": "getTickPrices",
	"streamSessionId": "",
	"symbol": "EURUSD",
	"minArrivalTime": 1,
	# "maxLevel": 2
}

ping_cmd = {
	"command": "ping",
	"streamSessionId": ""
}

get_keep_alive_cmd = {
	"command": "getKeepAlive",
	"streamSessionId": ""
}

ping = {
	"command": "ping"
}


def measure_execution(func: Callable[[], Any]):
    def wrapper():
        print(f"TIMER: execution started")
        start_time = time.time()
        res = func()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"TIMER: Execution time: {execution_time} seconds")
        return res
    return wrapper


def keep_alive(ws: websocket.WebSocketApp):
    global SESSION_ID
    while True:
        # cmd = ping_cmd
        # cmd["streamSessionId"] = SESSION_ID

        ws.send(json.dumps(ping))
        print(f"sending {ping}")
        time.sleep(1)


def on_message(ws: websocket.WebSocketApp, message: str):
    print(message)


def on_error(ws: websocket.WebSocketApp, error):
    print(error)


def on_close(ws: websocket.WebSocketApp, close_status_code, close_msg):
    print(f"close status code: {close_status_code}, close message {close_msg}")


def on_open(ws: websocket.WebSocketApp):
    global SESSION_ID
    get_keep_alive_cmd["streamSessionId"] = SESSION_ID
    ws.send(json.dumps(get_keep_alive_cmd))


@measure_execution
def main2():
    global SESSION_ID
    # cmd = get_ballance_cmd
    # cmd = get_tick_price
    cmd = get_keep_alive_cmd

    ws = create_connection("wss://ws.xtb.com/demo")
    print(f"ws: {ws.connected}")

    ws.send(json.dumps(login_cmd))
    result = json.loads(ws.recv())
    SESSION_ID = result["streamSessionId"]

    cmd["streamSessionId"] = SESSION_ID


    ws_stream = create_connection("wss://ws.xtb.com/demoStream")
    print(f"ws_stream: {ws_stream.connected}")

    ws_stream.send(json.dumps(cmd))
    # threading.Thread(target=keep_alive, args=(ws_stream,), daemon=True).start()
    threading.Thread(target=keep_alive, args=(ws,), daemon=True).start()
    try:
        while True:
            msg = ws_stream.recv()
            print(msg)
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        ws_stream.close()
        ws.close()


@measure_execution
def main():
    global SESSION_ID
    # cmd = get_ballance_cmd
    # cmd = get_tick_price
    # cmd = get_keep_alive_cmd
    # cmd["streamSessionId"] = SESSION_ID

    ws = create_connection("wss://ws.xtb.com/demo")
    print(f"ws: {ws.connected}")
    ws.send(json.dumps(login_cmd))
    result = json.loads(ws.recv())
    SESSION_ID = result["streamSessionId"]

    ws_stream = websocket.WebSocketApp("wss://ws.xtb.com/demoStream",
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
    # threading.Thread(target=keep_alive, args=(ws_stream,), daemon=True).start()
    ws_stream.run_forever()


def main():
    url = "wss://ws.xtb.com/demo"
    stream_url = "wss://ws.xtb.com/demoStream"
    client = XtbClient(client_id, password, url, stream_url)
    client.login()
    client.streaming_connect()
    # client.keep_alive()
    symbol = "ETHEREUM"
    # client.get_all_symbols()
    # client.get_symbol(symbol)
    client.get_chart_last_request(symbol, TimeStamp().now().sub_hr(2), Period.PERIOD_M1)
    # client.subscribe_to_get_keep_alive()
    # client.subscribe_to_get_tick_prices(symbol)
    # client.subscribe_to_get_balance()
    # client.subscribe_to_get_trades()
    # client.subscribe_to_get_candles(symbol)

    client.read_stream()

if __name__ == "__main__":
    main()
