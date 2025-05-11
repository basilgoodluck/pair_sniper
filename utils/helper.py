from datetime import datetime
import io
import sys
import os
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def plot_signals(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    buys = df[df['Signal'] == 1]
    sells = df[df['Signal'] == -1]

    plt.plot(buys.index, buys['Close'], '^', color='green', label='Buy Signal')
    plt.plot(sells.index, sells['Close'], 'v', color='red', label='Sell Signal')

    plt.title(f"Signals for {datetime.now().strftime('%Y-%m-%d')}")
    plt.legend()
    plt.grid()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

