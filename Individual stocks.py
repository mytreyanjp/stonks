from flask import Flask, jsonify
import yfinance as yf
import time
import threading
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

app = Flask(__name__)

# Stock settings
STOCK_SYMBOLS = ["AAPL", "GOOG", "TSLA", "AMZN"]
MONTH_DURATION = 5  # Each month lasts 5 seconds (adjustable)
YEARS = 20
TOTAL_MONTHS = YEARS * 12  # 20 years = 240 months

# Fetch historical data for each stock
def fetch_stock_data():
    stock_data = {}
    for symbol in STOCK_SYMBOLS:
        df = yf.download(symbol, period="5y", interval="1d")
        stock_data[symbol] = df['Close'].pct_change().dropna().values  # Percentage changes
    return stock_data

# Initialize stock prices and trends
historical_data = fetch_stock_data()
stocks = {
    symbol: {
        "price": round(yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1], 2),
        "history": [],
        "months": []  # Track months for X-axis
    }
    for symbol in STOCK_SYMBOLS
}

def update_stock_prices():
    """Simulates stock market changes and updates price history."""
    for month in range(1, TOTAL_MONTHS + 1):
        time.sleep(MONTH_DURATION)  # Wait for next month
        
        for symbol in stocks:
            pct_change = random.choice(historical_data[symbol]).item()
            stocks[symbol]["price"] = round(stocks[symbol]["price"] * (1 + pct_change), 2)
            stocks[symbol]["history"].append(stocks[symbol]["price"])
            stocks[symbol]["months"].append(month)  # Store month index

        print(f"\n Month {month}/{TOTAL_MONTHS} (Year {month // 12 + 1})")
        for symbol, data in stocks.items():
            print(f"  {symbol}: ${data['price']}")

# API endpoint for current stock prices
@app.route("/stocks", methods=["GET"])
def get_stocks():
    return jsonify(stocks)

# Start stock simulation in a background thread
threading.Thread(target=update_stock_prices, daemon=True).start()

### **Matplotlib Real-Time Graph (X-Axis = Months)**
fig, ax = plt.subplots()
lines = {symbol: ax.plot([], [], label=symbol)[0] for symbol in STOCK_SYMBOLS}
ax.set_xlabel("Months")
ax.set_ylabel("Stock Price")
ax.set_title("Real-Time Stock Price Simulation")
ax.legend()

def animate(i):
    """Updates the graph with the latest stock prices over time."""
    for symbol, line in lines.items():
        if stocks[symbol]["months"]:
            line.set_data(stocks[symbol]["months"], stocks[symbol]["history"])
    
    ax.relim()
    ax.autoscale_view()

# Start real-time graph update
ani = animation.FuncAnimation(fig, animate, interval=1000)  # Update every second

if __name__ == "__main__":
    plt.show()  # Open the live graph
    app.run(debug=True)
