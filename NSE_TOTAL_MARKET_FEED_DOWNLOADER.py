from datetime import datetime, time
from time import sleep
import requests 
import json
import pandas as pd
from pymongo import MongoClient

def getBaseCookies(url):
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) '
                      'Chrome/80.0.3987.149 Safari/537.36',
        'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br',
        'accept': '*/*', 'referer': url}
    session = requests.Session()
    response = session.get(url, headers=headers)
    cookies = dict(response.cookies)
    return session, cookies


def getReferalCookies(url,cookies):
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) '
                      'Chrome/80.0.3987.149 Safari/537.36',
        'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br',
        'accept': '*/*', 'referer': url}
    session = requests.Session()
    response = session.get(url, headers=headers,cookies=cookies)
    cookies = dict(response.cookies)
    return session, cookies


def getTotalMarketData():
    totalMarketURL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20TOTAL%20MARKET"
    refererURL = "https://www.nseindia.com/market-data/live-equity-market"
    baseurl = "https://www.nseindia.com/"
    session, cookies = getBaseCookies(baseurl)
    session, cookies = getReferalCookies(refererURL,cookies) 

    totlMktheaders = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                    'like Gecko) '
                    'Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br',
    'Content-Type':'application/json',
    'referer':'https://www.nseindia.com/market-data/live-equity-market'}

    #fut = session.get(url1, headers=headers).json()
    response = session.get(totalMarketURL, headers=totlMktheaders, timeout=5, cookies=cookies)
    print("STATUS CODE ---------------------------- ")
    print(response.status_code) 
    #txt =response.content # process_brotli_response(response.content)
    TotalMarketDataDF =pd.json_normalize(json.loads(response.content.decode('utf-8')))
    
    #print(TotalMarketData)
    TotalMarketData = TotalMarketDataDF['data'][0]
    return TotalMarketData

if __name__ == '__main__':
    # Get the current time
    current_time = datetime.now().time()
    # Define the start and end times for the loop
    start_time = time(9, 15)  # 9:15 AM
    end_time = time(15, 30)   # 3:30 PM

    # Loop until the current time is outside the specified range
    while start_time <= current_time <= end_time:
        df = getTotalMarketData()
        print("Data fetched successfully")
        #print(df)
        client = MongoClient("mongodb://localhost:27017/")
        
        # client =  MongoClient("mongodb+srv://<<YOUR USERNAME>>:<<PASSWORD>>@clustertest-icsum.mongodb.net/test?retryWrites=true&w=majority")
        db = client['NSE_TOTAL_MARKET']
        collection = db['LiveFeed']
        # data.reset_index(inplace=True)
        # data_dict = data.to_dict("records")
        # # Insert collection
        collection.insert_many(df)
        print("Data inserted into MongoDB "+ current_time.strftime("%H:%M:%S"))

        #df['timestamp'] = datetime.now()
        sleep(20)  # Wait for 20 seconds before the next request