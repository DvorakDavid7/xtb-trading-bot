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


def cmd_get_candles(stramSessionId: str, symbol: str) -> str:
    return json.dumps({
        "command": "getCandles",
        "streamSessionId": stramSessionId,
        "symbol": symbol
    })


def cmd_get_balance(stramSessionId: str) -> str:
    return json.dumps({
        "command": "getBalance",
        "streamSessionId": stramSessionId
    })


def cmd_get_all_symbols() -> str:
    return json.dumps({
        "command": "getAllSymbols"
    })


def cmd_get_trades(streamSessionId: str) -> str:
    return json.dumps({
        "command": "getTrades",
        "streamSessionId": streamSessionId
    })


def cmd_get_symbol(symbol: str) -> str:
    return json.dumps({
        "command": "getSymbol",
        "arguments": {
            "symbol": symbol
        }
    })

def cmd_get_tick_prices(streamSessionId: str, symbol: str) -> str:
    return json.dumps({
        "command": "getTickPrices",
        "streamSessionId": streamSessionId,
        "symbol": symbol,
        "minArrivalTime": 1,
        "maxLevel": 2
    })

def cmd_get_chart_last_request(symbol: str):
    return json.dumps({
        "command": "getChartLastRequest",
        "arguments": {
            "info": {
                "period": 5,
                "start": 1726520132,
                "symbol": symbol
            }
        }
    })