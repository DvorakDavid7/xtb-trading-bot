import json
from typing import Any
import websocket


get_ballance_cmd = {
	"command": "getBalance",
	"streamSessionId": ""
}

STREAM_SESSION_ID = ""


def create_streaming_connection(stream_session_id: str) -> None:
    global STREAM_SESSION_ID

    STREAM_SESSION_ID = stream_session_id

    ws = websocket.WebSocketApp("wss://ws.xtb.com/demoStream:5125",
                        on_open=on_open,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_close)
    ws.run_forever()

def on_message(ws: websocket.WebSocketApp, message: str):
    msg: dict[str, Any] = json.loads(message)
    print(msg)

def on_error(ws: websocket.WebSocketApp, error):
    print(error)

def on_close(ws: websocket.WebSocketApp, close_status_code, close_msg):
    print(f"close status code: {close_status_code}, close message {close_msg}")

def on_open(ws: websocket.WebSocketApp):
    global STREAM_SESSION_ID
    get_ballance_cmd["streamSessionId"] = STREAM_SESSION_ID
    ws.send(json.dumps(get_ballance_cmd))
