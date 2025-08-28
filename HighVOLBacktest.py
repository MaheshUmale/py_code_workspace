import pandas as pd
import numpy as np
import time
import concurrent.futures
import xlsxwriter
from tvDatafeed import TvDatafeed, Interval
import sqlite3

# Config
RESULTS_CSV = "high_vol_backtest_results.csv"
RESULTS_XLSX = "high_vol_backtest_dashboard.xlsx"
DB_FILE = "stock_data.db"
VOLUME_MULTIPLIER = 5
MIN_VALUE_CR = 7  # Crore
EOD_CUT_OFF = "15:15"
targetRMultiplier = 8
RISK_PER_TRADE = 10000
CAPITAL_PER_TRADE=200000
# Connect to TradingView
tv = TvDatafeed()

# Local DB setup
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS stock_data (
    symbol TEXT,
    datetime TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    PRIMARY KEY(symbol, datetime)
)""")
conn.commit()

def fetch_data(symbol):
    print(f" ----fetching {symbol} --")
    try:
        conn = sqlite3.connect(DB_FILE)
        df = tv.get_hist(symbol, "NSE", interval=Interval.in_1_minute, n_bars=5000)
        if df is None or df.empty:
            return None
        df.reset_index(inplace=True)
        df["symbol"] = symbol
        df.to_sql("stock_data", conn, if_exists="append", index=False)
        conn.close()
        time.sleep(2)
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None


# Strategy backtest
def backtest_symbol(symbol):
    try:
        # Try from DB first
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql(f"SELECT * FROM stock_data WHERE symbol='{symbol}'", conn)
        conn.close()
        print(f" ----checking db {symbol} --")
        if df.empty:
            df = fetch_data(symbol)
        if df is None or df.empty:
            return None

        df["value_cr"] = (df["close"] * df["volume"]) / 1e7
        df["vol_avg"] = df["volume"].rolling(200).mean()

        trades = []
        for i in range(200, len(df)):
            if df["value_cr"].iloc[i] >= MIN_VALUE_CR and df["volume"].iloc[i] >= VOLUME_MULTIPLIER * df["vol_avg"].iloc[i]:
                entry_price = df["close"].iloc[i]
                sl_price = df["low"].iloc[i] if df["close"].iloc[i] > df["open"].iloc[i] else df["high"].iloc[i]
                risk = entry_price - sl_price if df["close"].iloc[i] > df["open"].iloc[i] else sl_price - entry_price
                target = entry_price + targetRMultiplier * risk if df["close"].iloc[i] > df["open"].iloc[i] else entry_price - targetRMultiplier * risk
                quantity = 1
                if risk>0:
                    quantity = int(RISK_PER_TRADE/risk)
                    if quantity * entry_price > CAPITAL_PER_TRADE :
                        quantity = int(CAPITAL_PER_TRADE/entry_price)
                initial_sl_price =sl_price

                # Intraday filter
                trade_time = pd.to_datetime(df["datetime"].iloc[i])
                if trade_time.strftime("%H:%M") > EOD_CUT_OFF:
                    continue

                # Check exit condition before EOD
                for j in range(i+1, len(df)):
                    #trailing SL 
                    if df["close"].iloc[i] > df["open"].iloc[i] :
                        sl_price =  max(sl_price, df["low"].iloc[j-2]) 
                    if df["open"].iloc[i] > df["close"].iloc[i] :
                        sl_price =  min(sl_price, df["high"].iloc[j-2])

                    t = pd.to_datetime(df["datetime"].iloc[j])
                    if t.strftime("%H:%M") >= EOD_CUT_OFF:
                        trades.append({
                            "Symbol": symbol,
                            "EntryTime": df["datetime"].iloc[i],
                            "ExitTime": df["datetime"].iloc[j],                            
                            "Type": "Long" if df["close"].iloc[i] > df["open"].iloc[i] else "Short",
                            "EntryPrice": entry_price,
                            "ExitPrice": df["close"].iloc[j],
                            "PnL": quantity *( df["close"].iloc[j] - entry_price if df["close"].iloc[i] > df["open"].iloc[i] else entry_price - df["close"].iloc[j]),
                            "Quantity" :quantity,
                            "Initial_SL" :initial_sl_price
                        })
                        break
                        
                    if df["close"].iloc[i] > df["open"].iloc[i] and  (df["high"].iloc[j] >= target or df["low"].iloc[j] <= sl_price):
                        trades.append({
                            "Symbol": symbol,
                            "EntryTime": df["datetime"].iloc[i],
                            "ExitTime": df["datetime"].iloc[j],
                            "Type": "Long",                            
                            "EntryPrice": entry_price,
                            "ExitPrice": target if df["high"].iloc[j] >= target else sl_price,
                            "PnL":quantity *( (target - entry_price) if df["high"].iloc[j] >= target else (sl_price - entry_price)),
                            "Quantity" :quantity,
                            "Initial_SL" :initial_sl_price
                        })
                        break 
                        
                    if df["open"].iloc[i] > df["close"].iloc[i] and  (df["low"].iloc[j] <= target or df["high"].iloc[j] >= sl_price):
                        trades.append({
                            "Symbol": symbol,
                            "EntryTime": df["datetime"].iloc[i],
                            "ExitTime": df["datetime"].iloc[j],
                            "Type": "Short",                        
                            "EntryPrice": entry_price,
                            "ExitPrice": target if df["low"].iloc[j] <= target else sl_price,
                            "PnL": quantity *( ( entry_price - target) if df["low"].iloc[j] <= target else ( entry_price -sl_price)),
                            "Quantity" :quantity,
                            "Initial_SL" :initial_sl_price
                        })
                        break
        return trades

    except Exception as e:
        print(f"❌ Error backtesting {symbol}: {e}")
        return None

# Save CSV
def save_results_to_csv(results_list):
    df = pd.DataFrame(results_list)
    df.to_csv(RESULTS_CSV, index=False)
    print(f"✅ Results saved to {RESULTS_CSV}")
    return df

# Create Excel Dashboard
def create_excel_dashboard(df):
    workbook = xlsxwriter.Workbook(RESULTS_XLSX)
    worksheet = workbook.add_worksheet("Summary")

    # Aggregated summary
    summary = df.groupby("Symbol").agg(
        Trades=("PnL", "count"),
        Wins=("PnL", lambda x: (x > 0).sum()),
        Losses=("PnL", lambda x: (x <= 0).sum()),
        WinRate=("PnL", lambda x: (x > 0).mean()),
        TotalPnL=("PnL", "sum")
    ).reset_index()

    # Write summary
    for col_num, col_name in enumerate(summary.columns):
        worksheet.write(0, col_num, col_name)
        for row_num, value in enumerate(summary[col_name], start=1):
            worksheet.write(row_num, col_num, value)

    header_fmt = workbook.add_format({"bold": True, "bg_color": "#DCE6F1"})
    worksheet.set_row(0, None, header_fmt)

    percent_fmt = workbook.add_format({"num_format": "0.00%"})
    worksheet.set_column(4, 4, 12, percent_fmt)

    # Chart 1: Trades per Symbol
    chart1 = workbook.add_chart({"type": "column"})
    chart1.add_series({
        "name": "Trades",
        "categories": f"=Summary!$A$2:$A${len(summary)+1}",
        "values": f"=Summary!$B$2:$B${len(summary)+1}"
    })
    chart1.set_title({"name": "Trades per Symbol"})
    worksheet.insert_chart("H2", chart1)

    # Chart 2: Profit by Symbol
    chart2 = workbook.add_chart({"type": "bar"})
    chart2.add_series({
        "name": "TotalPnL",
        "categories": f"=Summary!$A$2:$A${len(summary)+1}",
        "values": f"=Summary!$F$2:$F${len(summary)+1}"
    })
    chart2.set_title({"name": "Profit by Symbol"})
    worksheet.insert_chart("H20", chart2)

    workbook.close()
    print(f"✅ Excel dashboard saved to {RESULTS_XLSX}")

# Main Pipeline
if __name__ == "__main__":
    # Example: Replace with NSE stock list fetch
    symbols = pd.read_csv("nse_stocks.csv")['Symbol'].tolist() #["RELIANCE", "INFY", "TCS"]

    all_trades = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(backtest_symbol, sym): sym for sym in symbols}
        for future in concurrent.futures.as_completed(futures):
            trades = future.result()
            if trades:
                all_trades.extend(trades)

    if all_trades:
        df_results = save_results_to_csv(all_trades)
        create_excel_dashboard(df_results)
