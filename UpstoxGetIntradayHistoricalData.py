import upstox_client
from upstox_client.rest import ApiException

import json


api_version = '2.0'
access_token = ''
instrumentKeys = ["NSE_INDEX|Nifty Bank", "NSE_INDEX|Nifty 50", "NSE_FO|35415", "NSE_FO|35165", "NSE_FO|35006", "NSE_FO|35080"]

api_instance = upstox_client.HistoryApi()
#instrument_key = 'NSE_EQ|INE669E01016'
interval = '1minute'
for instrument_key in instrumentKeys:
    try:
        api_response = api_instance.get_intra_day_candle_data(instrument_key,interval,api_version)
        print(api_response)
        with open("intraday_HIST_1Min_"+instrument_key.split('|')[1]+"output.json", "a") as f:
            f.write(str(api_response))
            f.flush()

    except ApiException as e:
        print("Exception when calling HistoryApi->get_historical_candle_data: %s\n" % e)


