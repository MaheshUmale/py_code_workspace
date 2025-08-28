
from time import sleep
from datetime import datetime
from tradingview_screener import Query, col
# Set display options to prevent column wrapping
import pandas as pd
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0) # Adjust as needed, 0 will use the full available width
master_combined =  pd.DataFrame()

import pandas as pd
import os

def append_df_to_csv(df, csv_path):
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=True, index=False)
    else:
        df.to_csv(csv_path, mode='a', header=False, index=False)


writeHeader=True
while True :
    df_combined = pd.DataFrame() 

    tvQuery = Query().set_markets('india') 
    _,dfNew = (tvQuery
      .select('name', 'close', 'volume', 'volume|1','relative_volume_10d_calc|1', 'relative_volume_10d_calc|5','relative_volume_intraday|5','average_volume_60d_calc|1')#'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
        .where(     
            col('average_volume_10d_calc')>1000000,           
            col('volume|1') > 100000,
            col('volume|1')  < col('volume') 
        ) 
    .order_by('volume|1', ascending=False)
    
    .get_scanner_data())
 
    current_DATE = datetime.now().strftime('%d_%m_%y')
    current_time = datetime.now().strftime('%H:%M:%S')
    from time import sleep
    from datetime import datetime
    if not dfNew.empty :
        current_time = datetime.now().strftime('%H:%M:%S')
        current_DATE = datetime.now().strftime('%d_%m_%y')
        dfNew.insert(3, 'URL',"") 
        dfNew['URL'] = "https://in.tradingview.com/chart/N8zfIJVK/?symbol="+dfNew['ticker']+" "
        # Insert the current time as a new column at the beginning of the DataFrame
        dfNew.insert(0, 'current_timestamp', current_time)
        # dfNew['dateTime'] = current_time
        append_df_to_csv(dfNew, 'TimeBasedAlerts_'+str(current_DATE)+'.csv') #dfNew.to_csv('TimeBasedAlerts_'+str(current_DATE)+'.csv', mode='a', index=False, header=False)
        df_combined = pd.concat([df_combined, dfNew], ignore_index=True)
        writeHeader=False
    #sleep5)  
 
    tvQuery = Query().set_markets('india') 
    _,dfNew = (tvQuery
     .select('name', 'close', 'volume', 'volume|1','volume|5','relative_volume_10d_calc|1', 'relative_volume_10d_calc|5','relative_volume_intraday|5','average_volume_60d_calc|1','average_volume_60d_calc|5')#'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
    .where(      #col('relative_volume_10d_calc') > 1,
            # col('relative_volume_intraday|5') > 1.2,
            # col('volume_change|5') > 0.2,
            col('volume')> col('average_volume_60d_calc|1'),
            
            col('VWAP|1')>col('VWAP|5'),
            col('VWAP|1')>col('VWAP|15'),
         
            col('volume|1') > 100000,
            col('volume|1')  < col('volume') 
        )
    # .order_by('relative_volume_intraday|5', ascending=False)
    .order_by('volume|1', ascending=False)
    
    .get_scanner_data())

    # append_df_to_csv(dfNew, 'TimeBasedAlerts_VWAP_'+str(current_DATE)+'.csv')
    # df = df._append(dfNew)
    
    from time import sleep
    from datetime import datetime

    if not dfNew.empty :
        current_time = datetime.now().strftime('%H:%M:%S')
        
        current_DATE = datetime.now().strftime('%d_%m_%y')

        # dfNew.insert(2, 'baseURL', "https://in.tradingview.com/chart/N8zfIJVK/?symbol="+str(dfNew['ticker'])+"") 
        # Insert the current time as a new column at the beginning of the DataFrame
        dfNew.insert(3, 'URL',"") 
        dfNew['URL'] = "https://in.tradingview.com/chart/N8zfIJVK/?symbol="+dfNew['ticker']+" "

        dfNew.insert(0, 'current_timestamp', current_time)
        # Filter rows where col1 is 3 times col2
        # 
        filtered_df = dfNew[dfNew['volume|5'] > 2 * dfNew['average_volume_60d_calc|5']]
        if not filtered_df.empty :
            # dfNew['dateTime'] = current_time
            # filtered_df.to_csv('TimeBasedAlerts_VolSpike_'+str(current_DATE)+'.csv', mode='a', index=False, header=False)
            append_df_to_csv(filtered_df, 'TimeBasedAlerts_VolSpike_'+str(current_DATE)+'.csv')
            print(f"=="*30)
            # print(filtered_df)
            writeHeader=False
            df_combined = pd.concat([df_combined, dfNew], ignore_index=True)
    
    #sleep5)    

    tvQuery = Query().set_markets('india')#.set_index('SYML:NSE;CNX500') #INDEX
    # tvQuery.set_markets('india') #MARKET
    #'indexes','name', 'close', 'volume',
    _,dfNew = (tvQuery
    # .select('name', 'premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume','average_volume','relative_volume')#'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
        .select('name', 'close', 'volume', 'volume|1','relative_volume_10d_calc|1', 'relative_volume_10d_calc|5','relative_volume_intraday|5','average_volume_60d_calc|1') #'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
        .where(      #col('relative_volume_10d_calc') > 1,
                # col('relative_volume_intraday|5') > 1.2,
            # col('volume_change|5') > 0.2,
            col('average_volume_10d_calc')>1000000,
            
            col('VWMA|1')<col('VWMA|5'),
            col('VWMA|1')<col('VWMA|15'),
        
          
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
    from time import sleep
    from datetime import datetime
    if not dfNew.empty :
        current_time = datetime.now().strftime('%H:%M:%S')
        current_DATE = datetime.now().strftime('%d_%m_%y')
        dfNew.insert(3, 'URL',"") 
        dfNew['URL'] = "https://in.tradingview.com/chart/N8zfIJVK/?symbol="+dfNew['ticker']+" "
        # Insert the current time as a new column at the beginning of the DataFrame
        dfNew.insert(0, 'current_timestamp', current_time)
        # dfNew['dateTime'] = current_time
        # dfNew.to_csv('TimeBasedAlertsVWAP_NEGATIVE_'+str(current_DATE)+'.csv', mode='a', index=False, header=False)
        
        append_df_to_csv(dfNew, 'TimeBasedAlertsVWAP_NEGATIVE_'+str(current_DATE)+'.csv')
        df_combined = pd.concat([df_combined, dfNew], ignore_index=True)
        writeHeader=False
    
    #sleep5)  
    tvQuery = Query().set_markets('india')#.set_index('SYML:NSE;CNX500') #INDEX
    # tvQuery.set_markets('india') #MARKET
    #'indexes','name', 'close', 'volume',
    _,dfNew = (tvQuery
    # .select('name', 'premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume','average_volume','relative_volume')#'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
    .select('name', 'close', 'volume', 'volume|1','relative_volume_10d_calc|1', 'relative_volume_10d_calc|5','relative_volume_intraday|5','average_volume_60d_calc|1')#'relative_volume_10d_calc','volume_change|1','relative_volume_intraday|5','relative_volume','VWMA','premarket_change','premarket_change_abs','premarket_change_from_open','premarket_change_from_open_abs','premarket_close','premarket_gap','premarket_high','premarket_low','premarket_open','premarket_volume')
    .where(       
            col('average_volume_10d_calc')>1000000,
            
            col('VWMA|1')>col('VWMA|5'),
            col('VWMA|1')>col('VWMA|15'), 
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
        # dfNew.to_csv('TimeBasedAlertsVWAP_POSITIVE_'+str(current_DATE)+'.csv', mode='a', index=False, header=False)
        
        append_df_to_csv(dfNew, 'TimeBasedAlertsVWAP_POSITIVE_'+str(current_DATE)+'.csv')

        df_combined = pd.concat([df_combined, dfNew], ignore_index=True)
        writeHeader=False
    
    #sleep5)   
    print(df_combined.tail(15))

    master_combined = pd.concat([master_combined, df_combined], ignore_index=True)

    # df_combined.to_csv('TimeBasedAlerts_COMBINED_'+str(current_DATE)+'.csv', mode='a', index=False, header=False)
    append_df_to_csv(df_combined, 'TimeBasedAlerts_COMBINED_'+str(current_DATE)+'.csv')
    if  current_time >= "15:29:59":#end_time_str:
        
        # master_combined.to_csv('TimeBasedAlerts_COMBINED_'+str(current_DATE)+'.csv', mode='a', index=False, header=True)
        break
    
    sleep(10)
 