


from tradingview_screener import Query, col

# tvQuery = Query().set_markets('india')#.set_index('SYML:NSE;CNX500') #INDEX
#     # tvQuery.set_markets('india') #MARKET
#     #'indexes','name', 'close', 'volume',
# _,dfNew = (tvQuery
#     .select('name', 'close', 'volume', 'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5',
#             'relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open',
#             'premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
#     .where(      #col('relative_volume_10d_calc') > 1,
#             # col('relative_volume_intraday|5') > 1.2,
#             # col('volume_change|5') > 0.2,
#             col('average_volume_10d_calc')>1000000,
#             # col('name')=='NSE:HINDMOTORS',
#             col('premarket_change') > 1,
#             # col('premarket_volume') > 100000,
#             col('premarket_change_abs')>1,
#             # col('VWMA') > 0.2,
#             # col('close') > 1000,
#             # col('market_cap_basic') > 100000000,
#             # col('market_cap_basic') < 1000000000000,    
#         )
#     .order_by('relative_volume_intraday|5', ascending=False)
#     .get_scanner_data(cookies=cookies))

# print(dfNew[['name','premarket_change_abs','premarket_gap']])

# Set display options to prevent column wrapping
import pandas as pd
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0) # Adjust as needed, 0 will use the full available width

writeHeader=True

while True :
    tvQuery = Query().set_markets('india')#.set_index('SYML:NSE;CNX500') #INDEX
    # tvQuery.set_markets('india') #MARKET
    #'indexes','name', 'close', 'volume',
    _,dfNew = (tvQuery
    # .select('name', 'premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume','average_volume','relative_volume')#'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
    .select('name', 'close', 'volume', 'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','average_volume','VWAP|1','VWAP|5','VWMA|5','VWMA|15')
    #'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
    .where(      #col('relative_volume_10d_calc') > 1,
            # col('relative_volume_intraday|5') > 1.2,
            # col('volume_change|5') > 0.2,
            col('average_volume_10d_calc')>1000000,
            
            col('VWMA|1')>col('VWMA|5'),
            col('VWMA|1')>col('VWMA|15'),
        
            # # col('name')=='NSE:HINDMOTORS',
            # col('premarket_gap') > 1,
            # col('premarket_change') > 1,
            # col('premarket_volume') > 100000,
            # col('premarket_change_abs')>1,
            # col('VWMA') > 0.2,
            # col('close') >col('VWAP|5') ,
            # col('market_cap_basic') > 100000000,
            # col('market_cap_basic') < 1000000000000,    
            col('volume|1') > 100000,
            col('volume|1')  < col('volume') 
        )
    # .order_by('relative_volume_intraday|5', ascending=False)
    .order_by('volume|1', ascending=False)
    
    .get_scanner_data())

    # df = df._append(dfNew)
    from time import sleep
    from datetime import datetime
    current_DATE = datetime.now().strftime('%d_%m_%y')
    current_time = datetime.now().strftime('%H:%M:%S')
    
    if not dfNew.empty :
        
        dfNew.insert(3, 'URL',"") 
        dfNew['URL'] = "https://in.tradingview.com/chart/N8zfIJVK/?symbol="+dfNew['ticker']+" "
        # Insert the current time as a new column at the beginning of the DataFrame
        dfNew.insert(0, 'current_timestamp', current_time)
        # dfNew['dateTime'] = current_time
        dfNew.to_csv('TimeBasedAlertsVWAP_POSITIVE_'+str(current_DATE)+'.csv', mode='a', index=False, header=False)
        print(dfNew)
        writeHeader=False
    
    sleep(10)   
    if  current_time >= "15:29:59":#end_time_str:
        break

# from datetime import datetime