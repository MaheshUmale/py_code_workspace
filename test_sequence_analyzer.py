import pandas as pd
import numpy as np
from candlestick_sequence_analyzer import CandlestickSequenceAnalyzer

# Create sample data
def generate_sample_data(n_periods=100):
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=n_periods, freq='1min')
    
    # Generate prices with some trend and volatility
    base_price = 100
    volatility = 0.002
    trend = 0.0001
    
    prices = [base_price]
    for i in range(n_periods-1):
        price_change = np.random.normal(trend, volatility)
        prices.append(prices[-1] * (1 + price_change))
    
    # Generate OHLCV data
    df = pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'Close': [p * (1 + np.random.normal(0, 0.001)) for p in prices],
        'Volume': np.random.randint(1000, 5000, n_periods)
    })
    
    # Calculate High and Low with some randomness
    df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.001, n_periods)))
    df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.001, n_periods)))
    
    return df


#LOAD ALL DATA
import sqlite3
import pandas as pd
import datetime
import os


dbFile ='D:\\py_code_workspace\\NSE_DATA_PROCESSING\\DATA\\NSE_1min_DATA.sqlite.db'

def getSymbolsData(symbol):
    symbol = symbol.upper()
    if not os.path.exists(dbFile):
        print("File does not exist")
        return None
    conn = sqlite3.connect(dbFile)
    #conn = sqlite3.connect('.\\NSE_MASTER_DATA.sqlite.db')
    df = pd.read_sql_query("SELECT  * FROM  '"+symbol+"' ", conn)
    conn.close()
    return df


###
### START FROM HERE 
# data = getSymbolsData("FACT-EQ")

def main():
    # Generate sample data
    df = getSymbolsData("FACT-EQ")
    
    # Initialize analyzer
    analyzer = CandlestickSequenceAnalyzer()
    
    # Calculate features and identify patterns
    patterns = analyzer.identify_patterns(df)
    print("\nMost common patterns:")
    for pattern, count in patterns.most_common(5):
        print(f"Pattern occurred {count} times:")
        for i, candle in enumerate(pattern):
            print(f"Candle {i+1}: Size={candle[0]}, Volume={candle[1]}, Equal_Lows={candle[2]}, Equal_Highs={candle[3]}, Higher_High={candle[4]}, Lower_Low={candle[5]}, Consec_HH={candle[6]}, Consec_LL={candle[7]}")
    
    # Make predictions
    predictions = analyzer.predict_next_candles(df)
    if predictions:
        print("\nPredicted next 3 candles:")
        for i, pred in enumerate(predictions):
            print(f"\nCandle {i+1}:")
            print(f"Open: {pred['Open']:.2f}")
            print(f"High: {pred['High']:.2f}")
            print(f"Low: {pred['Low']:.2f}")
            print(f"Close: {pred['Close']:.2f}")
            print(f"Confidence: {pred['Confidence']:.2%}")
        
        # Plot patterns and predictions
        fig = analyzer.plot_patterns_and_predictions(df, predictions)
        fig.show()
    else:
        print("\nNo predictions made.")

if __name__ == "__main__":
    main()