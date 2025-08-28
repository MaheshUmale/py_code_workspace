# First, ensure you have the necessary libraries installed
# pip install tradingview-screener pandas yfinance
from time import sleep
from datetime import datetime
from tradingview_screener import Query, col
from tradingview_screener import Query, col
import pandas as pd
import yfinance as yf

from tvDatafeed import TvDatafeed, Interval
# ==============================================================================
# SECTION 1: Previous custom logic remains the same
# (Keep all the functions from the first response: get_pivots_vectorized,
# apply_scanner_logic, etc.)
# ... (all previous Python functions go here) ...
# ==============================================================================


HIGH_VALUE = 10000000.00
VOLUME_MULTIPLIER =  2.0

def get_pivots_vectorized(df: pd.DataFrame, pivot_lookup: int) -> pd.DataFrame:
    """
    Identifies pivot points and calculates the 'top' and 'bottom' value lines.
    This is a vectorized Python equivalent of Pine Script's `ta.pivothigh`,
    `ta.pivotlow`, and `ta.valuewhen` logic.

    Args:
        df: DataFrame with OHLC data.
        pivot_lookup: The number of bars to look back and forward for a pivot.

    Returns:
        DataFrame with 'top' and 'bottom' columns added.
    """
    # Calculate rolling window to find the max/min in a centered window
    # A bar is a pivot if its high/low is the maximum/minimum in its window
    high_roll = df["high"].rolling(window=2 * pivot_lookup + 1, center=True).max()
    low_roll = df["low"].rolling(window=2 * pivot_lookup + 1, center=True).min()

    # Identify pivot bars
    is_pivot_high = df["high"] == high_roll
    is_pivot_low = df["low"] == low_roll

    # Get the price at the pivot bar
    pivot_high_price = df["high"][is_pivot_high]
    pivot_low_price = df["low"][is_pivot_low]

    # Replicate Pine Script's plotting delay. A pivot at index `i` is
    # only confirmed at index `i + pivot_lookup`.
    df["pivot_high_event"] = pivot_high_price.shift(pivot_lookup)
    df["pivot_low_event"] = pivot_low_price.shift(pivot_lookup)

    # Forward-fill to replicate ta.valuewhen, creating the 'top' and 'bottom' lines
    df["top"] = df["pivot_high_event"].ffill()
    df["bottom"] = df["pivot_low_event"].ffill()

    # Clean up intermediate columns
    return df.drop(columns=["pivot_high_event", "pivot_low_event"])


def apply_scanner_logic(df: pd.DataFrame, pivot_lookup: int = 1) -> pd.DataFrame:
    """
    Applies all the trading logic from the Pine Script to a DataFrame.

    Args:
        df: DataFrame with OHLC data.
        pivot_lookup: The lookup period for pivot calculations.

    Returns:
        DataFrame with boolean columns for each detected condition.
    """
    # --- Helper Conditions ---
    is_up = df["close"] > df["open"]
    is_down = df["close"] < df["open"]

    # --- Fair Value Gaps (FVG) ---
    is_fvg_up = df["low"] > df["high"].shift(2)
    is_fvg_down = df["high"] < df["low"].shift(2)

    # --- Order Blocks (OB) ---
    # Bullish OB: A down candle followed by an up candle that closes above the down candle's high.
    is_ob_up = is_down.shift(1) & is_up & (df["close"] > df["high"].shift(1))
    # Bearish OB: An up candle followed by a down candle that closes below the up candle's low.
    is_ob_down = is_up.shift(1) & is_down & (df["close"] < df["low"].shift(1))

    # --- 1. Premium/Discount Order Blocks (PPDD) ---
    df_pivots = get_pivots_vectorized(df.copy(), pivot_lookup)

    if "top" in df_pivots.columns and "bottom" in df_pivots.columns:
        high_sweep = df_pivots["high"].rolling(2).max()
        low_sweep = df_pivots["low"].rolling(2).min()

        # Liquidity sweep conditions
        cond_pp_sweep = (
            (high_sweep > df_pivots["top"]) & (df_pivots["close"] < df_pivots["top"])
        ) | (
            (high_sweep > df_pivots["top"].shift(1))
            & (df_pivots["close"] < df_pivots["top"].shift(1))
        )

        cond_dd_sweep = (
            (low_sweep < df_pivots["bottom"])
            & (df_pivots["close"] > df_pivots["bottom"])
        ) | (
            (low_sweep < df_pivots["bottom"].shift(1))
            & (df_pivots["close"] > df_pivots["bottom"].shift(1))
        )

        # PPDD (Premium Premium - Bearish)
        df["premium_premium"] = is_ob_down & cond_pp_sweep
        # PPDD (Discount Discount - Bullish)
        df["discount_discount"] = is_ob_up & cond_dd_sweep

        # Weak PPDD (Bearish)
        cond_pp_weak_candle = (
            is_up.shift(1) & is_down & (df["close"] < df["open"].shift(1))
        )
        df["premium_premium_weak"] = (
            cond_pp_weak_candle & cond_pp_sweep & (~df["premium_premium"])
        )

        # Weak PPDD (Bullish)
        cond_dd_weak_candle = (
            is_down.shift(1) & is_up & (df["close"] > df["open"].shift(1))
        )
        df["discount_discount_weak"] = (
            cond_dd_weak_candle & cond_dd_sweep & (~df["discount_discount"])
        )

    # --- 2. Single Candle Order Block (SCOB) ---
    # Bullish SCOB
    df["bull_scob"] = (
        (df["high"] > df["high"].shift(1))
        & (df["high"] > df["high"].shift(2))
        & (df["low"].shift(1) < df["low"].shift(2))
        & (df["low"].shift(1) < df["low"])
        & (is_down.shift(2))
        & (df["close"] > df["open"].shift(2))
        & (df["close"] > df["close"].shift(1))
    )

    # Bearish SCOB
    df["bear_scob"] = (
        (df["low"] < df["low"].shift(1))
        & (df["low"] < df["low"].shift(2))
        & (df["high"].shift(1) > df["high"].shift(2))
        & (df["high"].shift(1) > df["high"])
        & (is_up.shift(2))
        & (df["close"] < df["open"].shift(2))
        & (df["close"] < df["close"].shift(1))
    )

    # --- 3. Stacked OB + FVG ---
    # Note: The Pine Script used an undefined 'plotOBFVG' variable.
    # This logic is included directly here.
    df["bear_stacked_ob_fvg"] = is_fvg_down & is_ob_down.shift(1)
    df["bull_stacked_ob_fvg"] = is_fvg_up & is_ob_up.shift(1)
    print(is_fvg_down)
    return df.fillna(False)


# ==============================================================================
# SECTION 2: The New Hybrid Scanner
# ==============================================================================


def run_hybrid_scanner():
    """
    Executes the two-step scanning process.
    """
    # --- STEP 1: Broad Filtering with TradingView-Screener ---
    print("Step 1: Finding promising symbols with TradingView-Screener...")

    try:
        # Example: Find the top 100 most volatile US stocks with high relative volume
        
        # query =   Query().select(
        #         "name",  # Stock name
        #         "close",  # Current price
        #         "volume|5",  # 1-minute volume
        #         "Value.Traded|5",  # 1-minute traded value
        #         "average_volume_10d_calc",  # Average volume (10 days)
        #         "average_volume_10d_calc|5",  # Average 1-minute volume (10 days)
        #     )            .where(
        #         col("is_primary") == True,
        #         col("typespecs").has("common"),
        #         col("type") == "stock",
        #         col("exchange") == "NSE"
                
                
        #     )            .limit(100)             
        
        # _, screener_results = query.get_scanner_data()
                # Select the columns we want to display
        query = Query().select(
            'name',                    # Stock name
            'close',                   # Current price
            'volume|5',                # 1-minute volume
            'Value.Traded|5',          # 1-minute traded value
            'average_volume_10d_calc', # Average volume (10 days)
            'average_volume_10d_calc|5' # Average 1-minute volume (10 days)
        ).where(
            col('is_primary') == True,
            col('typespecs').has('common'),
            col('type') == 'stock',
            col('exchange') == 'NSE',
            col('close').between(2, 10000),
            col('active_symbol') == True, 
            col('volume|1') >col('average_volume_10d_calc|5'),
            col('Value.Traded|1') > HIGH_VALUE,

        ).order_by(
            'volume|1', ascending=False
        ).limit(100).set_markets('india').set_property(
            'preset', 'all_stocks'
        ).set_property(
            'symbols', {'query': {'types': ['stock', 'fund', 'dr']}}
        ) 
        # Execute the query
        _, screener_results = query.get_scanner_data()
        

        if screener_results is None or screener_results.empty:
            print("Could not retrieve initial list from TradingView-Screener. Exiting.")
            return

        candidate_symbols = screener_results["name"].tolist()
        print(f"Found {len(candidate_symbols)} candidate symbols.")

    except Exception as e:
        print(f"An error occurred during Step 1: {e}")
        return

    final_triggered_symbols = {}

    for symbol in candidate_symbols:
        sleep(1)
    # --- STEP 2: Deep Analysis with our Custom Logic ---
        print("\nStep 2: Performing deep analysis on candidate symbols..."+symbol)
        try:
            # Fetch historical data (e.g., using yfinance for stocks)
            # We need at least ~20 bars to have enough data for lookbacks
             
             # Initialize TvDatafeed
            tv = TvDatafeed()
            
            # Fetch data (assuming Indian stocks on NSE)
            # You may need to adjust the exchange based on the symbol
            exchange = 'NSE'  
            
            # Fetch 1-minute interval data
            ticker_data = tv.get_hist(symbol, exchange, interval=Interval.in_1_minute, n_bars=300)
            print(ticker_data.head())

            if ticker_data.empty or len(ticker_data) < 20:
                print(f"Skipping {symbol}: Not enough historical data.")
                continue

            # Rename columns to be compatible with our functions
            ticker_data.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                },
                inplace=True,
            )

            # Apply our detailed, multi-candle logic
            df_analyzed = apply_scanner_logic(ticker_data, pivot_lookup=1)

            
            for i in range(5):
                # Check the most recent candle for signals
                last_candle = df_analyzed.iloc[-i]
                conditions_met = [
                    col
                    for col in last_candle.index
                    if col.startswith(("bull", "bear", "premium", "discount"))
                    and last_candle[col] is True
                ]

                if conditions_met:
                    print(f"✅ FINAL SIGNAL for {symbol} ROW{i}: {conditions_met}")
                    final_triggered_symbols[symbol] = conditions_met
           

        except Exception as e:
            # This can happen if a symbol from TV is not found on yfinance, etc.
            # print(f"Could not process {symbol}: {e}")
            pass

    print("\n--- Hybrid Scan Complete ---")
    if final_triggered_symbols:
        for symbol, conditions in final_triggered_symbols.items():
            print(f"Symbol: {symbol}, Conditions Triggered: {', '.join(conditions)}")
    else:
        print("No symbols passed the deep analysis.")


# --- Run the scanner ---
if __name__ == "__main__":
    run_hybrid_scanner()
