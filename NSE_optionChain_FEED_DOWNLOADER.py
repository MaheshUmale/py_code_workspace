from datetime import datetime, time
from time import sleep
import requests 
import json
import pandas as pd
from pymongo import MongoClient
import traceback
import sys

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

oi_url = {
    "nifty": "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",
    "banknifty": "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY",
}

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "accept-language": "en,gu;q=0.9,hi;q=0.8",
    "accept-encoding": "gzip, deflate, br",
}


def get_oi_summery(FULLDATA):
    try:
        OptionChainDataDF = FULLDATA
        
        print("STATUS CODE -----------------OPTION OptionChainDataDF data ----------- ")

        print(OptionChainDataDF)
        total_oi_ce =OptionChainDataDF["filtered.CE.totOI"]
        total_oi_pe = OptionChainDataDF["filtered.PE.totOI"]
        underlying = OptionChainDataDF["records.underlyingValue"]
        total_pcr = total_oi_pe / total_oi_ce

        expiry = OptionChainDataDF["records.expiryDates"][0]

        weekly_put_oi, weekly_call_oi = 0, 0
        data = (OptionChainDataDF['records.data'])
        count = len(data[0])
        print("count", count)
    # Add a new column with the current timestamp   
        for d in data[0]:
            # print(d["expiryDate"])
            # print(d["strikePrice"])
            # print(expiry[0])
            # print(underlying)
        
        #for d in OptionChainDataDF["filtered.data"][0]:

            if (
                
                d["expiryDate"] == expiry[0]
                and abs(d["strikePrice"] - int(underlying[0])) < 1000
            ):
                # print(d["expiryDate"])
                # print(d["strikePrice"])
                # print(d["PE"]["changeinOpenInterest"])
                # print(d["CE"]["changeinOpenInterest"]) 
                weekly_put_oi += d["PE"]["changeinOpenInterest"]
                weekly_call_oi += d["CE"]["changeinOpenInterest"]
                # print("weekly_call_oi", weekly_call_oi)
                # print("weekly_put_oi", weekly_put_oi)   
                
        pcr = weekly_put_oi / weekly_call_oi
        jsonStr ='{"weekly_call_oi": '+str(weekly_call_oi)+', "weekly_put_oi": '+str(weekly_put_oi)+', "weekly_pcr": '+str(pcr)+', "total_pcr": '+str(float(total_pcr[0]))+', "underlying": '+str(float(underlying[0]))+', "time": "'+datetime.now().time().isoformat()+'"}'
        # res = {
        #     "weekly_ce_oi": weekly_call_oi,
        #     "weekly_pe_oi": weekly_put_oi,
        #     "weekly_pcr": float("{:.2f}".format(pcr)),
        #     "total_pcr": float("{:.2f}".format(total_pcr)),
        #     "underlying": underlying,
        #     "time": datetime.now().time().isoformat(),
        # }
        valid_json_string = "[" + jsonStr + "]" 
        print("valid_json_string", valid_json_string)
        # dbf =pd.json_normalize(json.loads(valid_json_string))
        # #dbf = json.dumps(valid_json_string, indent=4)
        # #myDict = dict(json.loads(dbf))
        # # python_dict = json.loads(jsonStr)
        # print("JSON String:")
        # # print(myDict)
        # #print("Python Dictionary:")
        # #print(python_dict)
        data_dict = json.loads(jsonStr)
        return data_dict

    except Exception as exc:
        logging.error(repr(exc))
        print(traceback.format_exc())

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


def getOptionChainData(OptionChainURL):
    refererURL = "https://www.nseindia.com/option-chain"
    baseurl = "https://www.nseindia.com/"
    session, cookies = getBaseCookies(baseurl)
    session, cookies = getReferalCookies(refererURL,cookies) 

    optionChainHeader = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                    'like Gecko) '
                    'Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br',
    'Content-Type':'application/json',
    'referer':'https://www.nseindia.com/market-data/live-equity-market'}

    #fut = session.get(url1, headers=headers).json()
    response = session.get(OptionChainURL, headers=optionChainHeader, timeout=5, cookies=cookies)
    print("STATUS CODE -----------------OPTION CHain----------- ")
    print(response.status_code) 
    #txt =response.content # process_brotli_response(response.content)
    OptionChainDataDF =pd.json_normalize(json.loads(response.content.decode('utf-8')))
    data = (OptionChainDataDF['records.data'])
    # Add a new column with the current timestamp   
    for row in data[0]:
        row['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Convert the data to a JSON string with indentation for readability        

    #print(TotalMarketData)
   
    OptionChainData = data
    return [OptionChainDataDF, OptionChainData]


from datetime import datetime, time

def is_time_between(start_time, end_time):
    """Checks if the current time is between start_time and end_time.

    Args:
        start_time (time): Start time object.
        end_time (time): End time object.
    
    Returns:
        bool: True if current time is between start and end time, False otherwise.
    """
    now = datetime.now().time()
    if start_time <= end_time:
        return start_time <= now <= end_time
    else: # handles cases where the range spans midnight, e.g., 23:00 - 04:00
        return start_time <= now or now <= end_time


if __name__ == '__main__':
    # Get the current time
    current_time = datetime.now().time()
    # Define the start and end times for the loop
    start_time = time(9, 15)  # 9:15 AM
    end_time = time(15, 30)   # 3:30 PM
    
    BNoptionChainURL = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
    NiftyOptionChainURL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

    # Loop until the current time is outside the specified range
    while is_time_between(start_time, end_time):
        [optChainDF,df] = getOptionChainData(BNoptionChainURL)
        print("Data fetched successfully BNIFTY")
        client = MongoClient("mongodb://localhost:27017/")
        db = client['OptionChainData']
        collection = db['BNOptionChain'] 
        collection.insert_many(df[0] )
        print("Data inserted into MongoDB BNOptionChain"+ current_time.strftime("%H:%M:%S"))

        current_time = datetime.now()
        formatted_date = current_time.strftime("%d_%m_%Y")

       
        client = MongoClient("mongodb://localhost:27017/")
        db = client['OptionChainData']
        collection = db['nifty_oi_'+formatted_date]
       
        collection.insert_one( get_oi_summery(optChainDF))
        print("Data inserted into MongoDB BNOptionChain"+ current_time.strftime("%H:%M:%S"))

        
       
        sleep(10) 

        [optChainDF,df]  = getOptionChainData(NiftyOptionChainURL)
        print("Data fetched successfully NIFTY")
        client = MongoClient("mongodb://localhost:27017/")
        db = client['OptionChainData']
        collection = db['NiftyOptionChain'] 
        collection.insert_many(df[0] )
        print("Data inserted into MongoDB NiftyOptionChain")

        client = MongoClient("mongodb://localhost:27017/")
        db = client['OptionChainData']
        collection = db['banknifty_oi_'+formatted_date]
         
        collection.insert_one(get_oi_summery(optChainDF))
        print("Data inserted into MongoDB BNOptionChain"+ current_time.strftime("%H:%M:%S"))

        #df['timestamp'] = datetime.now()
        sleep(20)  # Wait for 20 seconds before the next request