from flask import Flask, render_template, jsonify, request, send_from_directory
from tradingview_screener import Query, col
import pandas as pd
import json
import os
from tvDatafeed import TvDatafeed, Interval
import pytz
from datetime import datetime
import csv

import urllib.parse
 
app = Flask(__name__)

# Data structure to store unique stock rows for CSV export
current_DATE = datetime.now().strftime('%d_%m_%y')
unique_stocks = set()
csv_file_path = 'stock_data_'+str(current_DATE)+'.csv'

def initialize_csv():
    """Initialize the CSV file with headers if it doesn't exist"""
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'symbol', 'name', 'price', 'volume', 'value_traded', 'avg_volume_10d','URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
def append_df_to_csv(df, csv_path=csv_file_path):
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=True, index=False)
    else:
        df.to_csv(csv_path, mode='a', header=False, index=False)

# def save_stock_to_csv(stock_data):
#     """Save stock data to CSV file"""
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     # Write to CSV
#     with open(csv_file_path, 'a', newline='') as csvfile:
#         fieldnames = ['timestamp', 'symbol', 'name', 'price', 'volume', 'value_traded', 'avg_volume_10d','URL']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
#         # Write each stock data with timestamp
#         for stock in stock_data:
#             # Create a unique key for the stock
#             stock_key = f"{stock['symbol']}_{timestamp}"                    
#             if stock_key not in unique_stocks:
#                 unique_stocks.add(stock_key)
#                 writer.writerow({
#                     'timestamp': timestamp,
#                     'symbol': stock['symbol'],
#                     'name': stock['name'],
#                     'price': stock['price'],
#                     'volume': stock['volume'],
#                     'value_traded': stock['value_traded'],
#                     'avg_volume_10d': stock['avg_volume_10d'],
#                     'URL':stocks['URL']
#                 })

# Initialize the CSV file
initialize_csv()

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/stock_list_data')
def download_csv():
    return send_from_directory('.', csv_file_path)

def get_chart_data(symbol, n_bars=100):
    """
    Fetch chart data for a symbol using tvDatafeed
    """
    try:
        # Initialize TvDatafeed
        tv = TvDatafeed()
        
        # Fetch data (assuming Indian stocks on NSE)
        # You may need to adjust the exchange based on the symbol
        exchange = 'NSE' if symbol.endswith('-EQ') or symbol.endswith('-NS') else 'NSE'
        
        # Fetch 1-minute interval data
        data = tv.get_hist(symbol, exchange, interval=Interval.in_1_minute, n_bars=n_bars)
        print(data.head())
        data.index = data.index.tz_localize('UTC')
        
        # Convert the localized index to IST
        data.index = data.index.tz_convert('Asia/Kolkata')
        # 3. Convert index to Unix timestamp in milliseconds
        data.index = data.index.map(lambda x: int(x.timestamp() * 1000))
        print( "data.size")
        if data is not None and not data.empty:
            # Convert DataFrame to list of dictionaries
            chart_data = []
            for index, row in data.iterrows():
                chart_data.append({
                    'time': index, #.isoformat(),  # Convert timestamp to ISO format
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume']) if not pd.isna(row['volume']) else 0
                })
            return chart_data
        else:
            return []
    except Exception as e:
        print(f"Error fetching chart data for {symbol}: {e}")
        return []

def get_stock_data(filters=None):
    """
    Fetch stock data using the tradingview_screener library
    """
    try:
        # Define constants with default values
        HIGH_VALUE = 10000000.00  # 20 Crore
        VOLUME_MULTIPLIER = 3.0
        MIN_VOLUME=10000
        # Override constants with filter values if provided
        if filters:
            if 'high_value' in filters and filters['high_value']:
                HIGH_VALUE = float(filters['high_value']) * 10000000  # Convert Crores to actual value
            if 'volume_multiplier' in filters and filters['volume_multiplier']:
                VOLUME_MULTIPLIER = float(filters['volume_multiplier'])
        
        # Create a query for Indian markets
        query = Query().set_markets('india')
        
        # Select the columns we want to display
        query = query.select(
            'name',                    # Stock name
            'close',                   # Current price
            'volume|1',                # 1-minute volume
            'Value.Traded|1',          # 1-minute traded value
            'average_volume_10d_calc', # Average volume (10 days)
            'average_volume_10d_calc|1' # Average 1-minute volume (10 days)
        ).where(
            col('is_primary') == True,
            col('typespecs').has('common'),
            col('type') == 'stock',
            col('exchange') == 'NSE',
            col('volume|1') > MIN_VOLUME,
            col('close').between(2, 10000),
            col('active_symbol') == True,
            col('Value.Traded|1') > HIGH_VALUE,
        ).order_by('Value.Traded', ascending=False, nulls_first=False
        ).limit(100).set_markets('india').set_property(
            'preset', 'volume_leaders'
        ).set_property(
            'symbols', {'query': {'types': ['stock', 'fund', 'dr']}}
        )

#   'preset', 'all_stocks'
        
#  .where(
#      col('is_primary') == True,
#      col('typespecs').has('common'),
#      col('type') == 'stock',
#      col('close').between(2, 10000),
#      col('active_symbol') == True,
#  )
#  .order_by('Value.Traded', ascending=False, nulls_first=False)
#  .limit(100)
#  .set_markets('india')
#  .set_property('preset', 'volume_leaders')
#  .set_property('symbols', {'query': {'types': ['stock', 'fund', 'dr']}}))


        # Execute the query
        _, df = query.get_scanner_data()
        
        print(df.head())
        # Apply the second filter: volume that is specified times more than the average 1-minute volume in the last 10 days
        if not df.empty:
            df = df[df['volume|1'] > VOLUME_MULTIPLIER * df['average_volume_10d_calc|1']]
        
        # If we still have data, limit to 100 results again after filtering
        if not df.empty:
            df = df.head(100)
        
        df = df[~df.ticker.str.startswith('BSE:')]
        # Rename columns using a dictionary mapping old names to new names
        df_renamed = df.rename(columns={'ticker': 'symbol', 'close': 'price', 'volume|1': 'volume', 'Value.Traded|1': 'value_traded', 'average_volume_10d_calc|1': 'avg_volume_10d'})
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df_renamed['URL'] = "https://in.tradingview.com/chart/N8zfIJVK/?symbol="+df_renamed['symbol'].apply(urllib.parse.quote)+" "
        df_renamed.insert(0, 'timestamp', timestamp)
         
        print(df_renamed.head())
        append_df_to_csv(df_renamed)
        # # Convert DataFrame to list of dictionaries
        # stocks = []
        # for _, row in df.iterrows():
        #     # Handle NaN values by converting them to None (which becomes null in JSON)
        #     def handle_nan(value):
        #         if pd.isna(value):
        #             return None
        #         return value
            
        #     stock = {
        #         'symbol': row.get('ticker', 'N/A'),
        #         'name': row.get('name', 'N/A'),
        #         'price': round(handle_nan(row.get('close', 0)) or 0, 2),
        #         'volume': int(handle_nan(row.get('volume|1', 0)) or 0),
        #         'value_traded': handle_nan(row.get('Value.Traded|1', 0)),
        #         'avg_volume_10d': handle_nan(row.get('average_volume_10d_calc|1', 0))
        #     }
            
        #     # Exclude BSE stocks (those with BSE: prefix or .BO suffix)
        #     if not stock['symbol'].startswith('BSE:') and not stock['symbol'].endswith('.BO'):
        #         # Fetch chart data for the stock
        #         #stock['chart_data'] = get_chart_data(stock['symbol'])
        #         stocks.append(stock)
        #     else:
        #         stocks.append(stock)
        
        # # Save to CSV
    
        # stocks['encodedTicker'] = stocks['ticker'].apply(urllib.parse.quote)
        # stocks['URL'] = "https://in.tradingview.com/chart/N8zfIJVK/?symbol="+stocks['encodedTicker']+" "
        # save_stock_to_csv(stocks)
        
        return df_renamed
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        # Return sample data in case of error
        return [
            {"symbol": "ERROR", "name": "Error fetching data", "price": 0, "change": 0, "volume": 0,
             "relative_volume": 0, "market_cap": 0, "pe_ratio": 0, "dividend_yield": 0}
        ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/csv-data')
def csv_data_page():
    return render_template('csv_data.html')

@app.route('/api/stocks')
def get_stocks():
    """
    API endpoint to get stock data with optional filters
    """
    # Get filters from query parameters
    filters = {
        'price_min': request.args.get('price_min'),
        'price_max': request.args.get('price_max'),
        'high_value': request.args.get('high_value'),
        'volume_multiplier': request.args.get('volume_multiplier')
    }
    
    # Remove None values from filters
    filters = {k: v for k, v in filters.items() if v is not None}
    
    stocks = get_stock_data(filters)
    # return jsonify(stocks)
    json_output = stocks.to_json(orient="records") 
    return json_output

@app.route('/api/chart/<symbol>')
def get_chart(symbol):
    """
    API endpoint to get chart data for a specific symbol
    """
    # Get n_bars from query parameters, default to 100
    n_bars = request.args.get('n_bars', default=100, type=int)
    
    chart_data = get_chart_data(symbol, n_bars)
    return jsonify(chart_data)

@app.route('/api/filters')
def get_filters():
    """
    API endpoint to get available filters
    """
    filters = {
        "price": {"min": 0, "max": 100000},
        "volume": {"min": 0.01, "max": 1000000000},
        "relative_volume": {"min": 0.01, "max": 100},
        "market_cap": {"min": 0, "max": 1000000000000},
        "pe_ratio": {"min": 0, "max": 1000},
        "dividend_yield": {"min": 0, "max": 20}
    }
    return jsonify(filters)

@app.route('/api/csv-data')
def get_csv_data():
    """
    API endpoint to get CSV data as JSON
    """
    try:
        # # Read the CSV file
        # data = []
        # print(" reading file "+csv_file_path)
        # if os.path.exists(csv_file_path):
           
        #     with open(csv_file_path, 'r') as csvfile:
        #         reader = csv.DictReader(csvfile)
        #         for row in reader:
        #             # Exclude BSE stocks (those with BSE: prefix or .BO suffix)
        #             # symbol = row.get('symbol', '')
        #             # if not symbol.startswith('BSE:') and not symbol.endswith('.BO'):
        #                 # data.append(row)
        #             data.append(row)
        # return jsonify(data)
        df = pd.read_csv(csv_file_path)
        return df.to_json(orient="records") 
    except Exception as e:
        print(f"Error reading CSV data: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)


from datetime import datetime
import pytz # for Python < 3.9, or use zoneinfo for Python >= 3.9

def convert_utc_to_ist(utc_time_str):
  """
  Converts a UTC time string (e.g., '2025-08-11T13:50:00') to IST (Asia/Kolkata).

  Args:
    utc_time_str: The UTC time string in 'YYYY-MM-DDTHH:MM:SS' format.

  Returns:
    A datetime object representing the time in IST.
  """

  # 1. Parse the UTC string into a datetime object
  utc_datetime = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S') 

  # 2. Make the datetime object timezone-aware (as UTC)
  utc_datetime = pytz.utc.localize(utc_datetime) # Or use utc_datetime.replace(tzinfo=datetime.timezone.utc) for Python 3.9+

  # 3. Convert to IST (Asia/Kolkata)
  ist_timezone = pytz.timezone('Asia/Kolkata')
  ist_datetime = utc_datetime.astimezone(ist_timezone)

  return ist_datetime