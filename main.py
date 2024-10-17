import queue
import os
import time
import pandas as pd

from lightweight_charts import Chart
from dotenv import load_dotenv

from xtb_trading_bot.commands import Period
from xtb_trading_bot.time_utils import TimeStamp
from xtb_trading_bot.xtb_client import XtbClient
from xtb_trading_bot.charting import ChartingThread

load_dotenv()

client_id = os.getenv("USER_ID") or ""
password = os.getenv("PASSWORD") or ""
url = "wss://ws.xtb.com/demo"
stream_url = "wss://ws.xtb.com/demoStream"


def calculate_sma(df, period: int = 50) -> pd.DataFrame:
    return pd.DataFrame({
        "time": df["date"],
        f"SMA {period}": df["close"].rolling(window=period).mean()
    }).dropna()


def compute_sma(current_data: pd.Series, period) -> int:
    return current_data.rolling(window=period).mean().iloc[-1]  # Return last value


def create_line(chart: Chart, data: pd.DataFrame, label: str, color="rgba(214, 0, 0, 1)"):
    line = chart.create_line(label, color=color)
    line.set(data)

def main():
    data_queue = queue.Queue()
    chart = Chart()
    chart.legend(visible=True)

    # charting_thread = ChartingThread(chart, data_queue)
    # charting_thread.start()

    client = XtbClient(client_id, password, url, stream_url, data_queue)
    client.login()
    client.streaming_connect()
    symbol = "ETHEREUM"

    df = client.get_chart_last_request(symbol, TimeStamp().now().sub_hr(2), Period.PERIOD_M1)
    chart.set(df.head(1))


    sma_10 = calculate_sma(df, period=10)
    sma_20 = calculate_sma(df, period=20)

    create_line(chart, sma_10, "SMA 10", "rgba(255, 0, 0, 1)")
    create_line(chart, sma_20, "SMA 20", "rgba(0, 255, 0, 1)")

    chart.show()

    sma_10_arr = []
    sma_20_arr = []

    total = 10000

    for i in range(len(df)):
        current_data = df.iloc[:i+1]

        if len(current_data) > 20:
            sma_10 = compute_sma(current_data["close"], 10)
            sma_20 = compute_sma(current_data["close"], 20)

            sma_10_arr.append(sma_10)
            sma_20_arr.append(sma_20)

            if len(sma_10_arr) >= 2:
                price = current_data["close"].iloc[-1]
                if sma_10_arr[-2] < sma_20_arr[-2] and sma_10 > sma_20:
                    total -= price
                    chart.marker(text="buy")
                elif sma_10_arr[-2] > sma_20_arr[-2] and sma_10 < sma_20:
                    total += price
                    chart.marker(text="sell", shape="arrow_down")

        chart.update(current_data.iloc[-1])
        time.sleep(0.1)
    print(total)


    # client.get_all_symbols()
    # client.subscribe_to_get_tick_prices(symbol)
    # client.subscribe_to_get_balance()
    # client.subscribe_to_get_trades()
    # client.subscribe_to_get_candles(symbol)

    # client.subscribe_to_get_keep_alive()
    # client.keep_alive()
    # client.read_stream()

    input("press any key to exit")



if __name__ == "__main__":
    main()
