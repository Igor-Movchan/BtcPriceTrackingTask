import json
import time
import websocket
import numpy as np
from datetime import datetime
from collections import deque
import signal
import sys

# Global variables
price_history = deque(maxlen=10)
retries = 0
max_retries = 5
backoff = 1

# WebSocket URL for BTC/USDT trade data
ws_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1s"

def on_message(ws, message):
    global retries, backoff
    try:
        data = json.loads(message)
        candle = data["k"]
        price = float(candle["c"])
        timestamp = datetime.utcfromtimestamp(candle["t"] / 1000).strftime("%Y-%m-%dT%H:%M:%S")
        price_history.append(price)
        sma = np.mean(price_history) if len(price_history) == 10 else None
        sma_str = f", SMA(10): ${sma:,.2f}" if sma else ""
        print(f"[{timestamp}] BTC → USD: ${price:,.2f}{sma_str}")
        retries = 0
        backoff = 1
    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")

def on_signal_received(signal, frame):
    print("\nShutting down...")
    sys.exit(0)

def start_websocket():
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_signal_received)
    while True:
        try:
            start_websocket()
        except Exception as e:
            print(f"WebSocket error: {e}")
            retries += 1
            if retries > max_retries:
                print("Max retries reached. Continuing to attempt reconnect...")
                retries = 0
            time.sleep(backoff)
            backoff *= 2
