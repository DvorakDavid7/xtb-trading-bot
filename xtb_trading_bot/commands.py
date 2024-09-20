import json


def cmd_login(client_id: str, password: str) -> str:
    return json.dumps({
        "command": "login",
        "arguments": {
            "userId": client_id,
            "password": password,
            "appId": "",
            "appName": ""
        }
    })


def cmd_get_keep_alive(streamSessionId: str) -> str:
    return json.dumps({
        "command": "getKeepAlive",
        "streamSessionId": streamSessionId
    }) 


def cmd_ping() -> str:
    return json.dumps({
        "command": "ping"
    })


def cmd_ping_stream(stramSessionId: str) -> str:
    return json.dumps({
        "command": "ping",
        "streamSessionId": stramSessionId
    })


def cmd_get_candles(stramSessionId: str) -> str:
    return json.dumps({
        "command": "getCandles",
        "streamSessionId": stramSessionId,
        "symbol": "EURUSD"
    })


def cmd_get_balance(stramSessionId: str) -> str:
    return json.dumps({
        "command": "getBalance",
        "streamSessionId": stramSessionId
    })
