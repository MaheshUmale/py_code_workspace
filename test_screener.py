from tradingview_screener import Query, col
import pandas as pd

def get_stock_data(filters=None):
    """
    Fetch stock data using the tradingview_screener library
    """
    try:
        # Define constants with default values
        HIGH_VALUE = 200000000.00  # 20 Crore
        VOLUME_MULTIPLIER = 5.0
        
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
        )
        
        # Apply the specific filters as requested:
        # 1. Trading value of specified amount in 1 minute
        query = query.where(col('Value.Traded|1') > HIGH_VALUE)
        # Note: The second condition will be applied after fetching the data
        
        # Order by 1-minute volume descending (most active stocks first)
        query = query.order_by('volume|1', ascending=False)
        
        # Limit to 100 results to avoid overwhelming the UI
        query = query.limit(100)
        
        # Execute the query
        _, df = query.get_scanner_data()
        
        # Apply the second filter: volume that is specified times more than the average 1-minute volume in the last 10 days
        if not df.empty:
            df = df[df['volume|1'] > VOLUME_MULTIPLIER * df['average_volume_10d_calc|1']]
        
        # If we still have data, limit to 100 results again after filtering
        if not df.empty:
            df = df.head(100)
        
        # Convert DataFrame to list of dictionaries
        stocks = []
        for _, row in df.iterrows():
            # Handle NaN values by converting them to None (which becomes null in JSON)
            def handle_nan(value):
                if pd.isna(value):
                    return None
                return value
            
            stock = {
                'symbol': row.get('name', 'N/A'),
                'name': row.get('name', 'N/A'),
                'price': round(handle_nan(row.get('close', 0)) or 0, 2),
                'volume': int(handle_nan(row.get('volume|1', 0)) or 0),
                'value_traded': handle_nan(row.get('Value.Traded|1', 0)),
                'avg_volume_10d': handle_nan(row.get('average_volume_10d_calc|1', 0))
            }
            stocks.append(stock)
        
        return stocks
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        # Return sample data in case of error
        return [
            {"symbol": "ERROR", "name": "Error fetching data", "price": 0, "volume": 0,
             "value_traded": 0, "avg_volume_10d": 0}
        ]

# Test the function
try:
    print("Testing get_stock_data function...")
    stocks = get_stock_data()
    
    print("Function executed successfully!")
    print("Number of stocks:", len(stocks))
    print("\nFirst stock:")
    print(stocks[0] if stocks else "No stocks returned")
    
    # Print the JSON that would be returned by the API
    import json
    print("\nJSON output:")
    print(json.dumps(stocks[:3], indent=2))  # Print first 3 stocks
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()