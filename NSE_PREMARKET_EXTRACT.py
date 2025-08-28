import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
import json
from datetime import datetime

def fetch_nse_premarket_data():
    #url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    url2 = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"
    #url2 = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"


            ##/api/market-data-pre-open?key=NIFTY&csv=true&selectValFormat=crores

    baseurl = "https://www.nseindia.com/"
    #url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'deflate'}
    session = requests.Session()
    request = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    #response = session.get(url, headers=headers, timeout=5, cookies=cookies)
    fn = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = fn+"premkt.json"
    try:
        # Fetch the data
        response = session.get(url2,headers=headers, timeout=5, cookies=cookies)
        response.raise_for_status()  # Raise an error for bad status codes
        if response.status_code == 200:
            print('response received')

    
            with open(filename, "wb") as f:
                f.write(response.content)
                print("CSV file downloaded successfully")
            
            # Read the CSV file into a Pandas DataFrame
            

            with open(filename) as f:
                d = json.load(f)
                #print(d['data'])
                #df = pd.json_normalize(d['data'])
                df = pd.DataFrame(d['data'])
                return df['metadata']
        else:
            print(f'Request failed with status code: {response.status_code}')
        return df
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def export_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data exported to {filename}")

def plot_top_stocks(data, top_n=10):
    # Filter top stocks based on percentage change
    sorted_data = sorted(data, key=lambda x: float(x["pChange"]), reverse=True)[:top_n]

    # Prepare data for plotting
    symbols = [stock["symbol"] for stock in sorted_data]
    percentage_changes = [float(stock["pChange"]) for stock in sorted_data]

    # Create bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(symbols, percentage_changes, color="skyblue")
    plt.xlabel("Percentage Change")
    plt.ylabel("Stock Symbol")
    plt.title(f"Top {top_n} Stocks by Percentage Change")
    plt.gca().invert_yaxis()  # Invert y-axis for better readability
    plt.show()

# Main program
premarket_stocks = fetch_nse_premarket_data()
# Export data to Excel
if len(premarket_stocks)>0:
    fn = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #export_to_excel(premarket_stocks, fn+"premarket_data.xlsx")

    # Plot top 10 stocks
    plot_top_stocks(premarket_stocks, top_n=20)
