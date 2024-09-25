import json
import time
from enum import Enum

from xtb_trading_bot.time_utils import TimeStamp

class Period(Enum):
    PERIOD_M1 =	1  # 1 minute
    PERIOD_M5 =	5  # 5 minutes
    PERIOD_M15 = 15  # 15 minutes
    PERIOD_M30 = 30  # 30 minutes
    PERIOD_H1 =	60  # 60 minutes (1 hour)
    PERIOD_H4 =	240  # 240 minutes (4 hours)
    PERIOD_D1 =	1440  #	1440 minutes (1 day)
    PERIOD_W1 =	10080  # 10080 minutes (1 week)
    PERIOD_MN1 = 43200  # 43200 minutes (30 days)


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

def cmd_get_chart_last_request(symbol: str, start: TimeStamp, period: Period):
    return json.dumps({
        "command": "getChartLastRequest",
        "arguments": {
            "info": {
                "period": period.value,
                "start": start.value(),
                "symbol": symbol
            }
        }
    })
