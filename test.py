# # Import libraries
# import requests
# from bs4 import BeautifulSoup

# url = "https://download.library.lol/main/3134000/987aa4b8f2563feccb1f3e4695914fc3/Al%20Brooks%20-%20Reading%20Price%20Charts%20Bar%20by%20Bar_%20The%20Technical%20Analysis%20of%20Price%20Action%20for%20the%20Serious%20Trader-Wiley%20%282009%29.pdf"
# name = "Al Brooks - Reading Price Charts Bar by Bar_ The Technical Analysis of Price Action for the Serious Trader-Wiley (2009).pdf"
# #
# # response = requests.get( url)
# # pdf = open(url, 'wb')
# # pdf.write(response.content)
# # pdf.close()
# response = requests.get(url, stream=True)
# with open(name, mode="wb") as file:
#     for chunk in response.iter_content(chunk_size=10 * 1024):
#         file.write(chunk)

# print( " DOWNLOADED ---"+name)




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
tvQuery = Query().set_markets('india')#.set_index('SYML:NSE;CNX500') #INDEX
    # tvQuery.set_markets('india') #MARKET
    #'indexes','name', 'close', 'volume',
_,dfNew = (tvQuery
 .select(
     'name',
     'description',
     'logoid',
     'update_mode',
     'type',
     'typespecs',
     'market_cap_basic',
     'fundamental_currency_code',
     'close',
     'pricescale',
     'minmov',
     'fractional',
     'minmove2',
     'currency',
     'change',
     'volume',
     'price_earnings_ttm',
     'earnings_per_share_diluted_ttm',
     'earnings_per_share_diluted_yoy_growth_ttm',
     'dividends_yield_current',
     'sector.tr',
     'sector',
     'market',
     'recommendation_mark',
     'relative_volume_10d_calc',
 )
 .where(
     col('is_primary') == True,
     col('typespecs').has('common'),
     col('type') == 'stock',
     col('close').between(2, 10000),
     col('change') > 0,
     col('active_symbol') == True,
 )
 .order_by('change', ascending=False, nulls_first=False)
 .limit(100)
 .set_markets('india')
 .set_property('symbols', {'query': {'types': ['stock', 'fund', 'dr']}})
 .set_property('preset', 'gainers')
 .get_scanner_data())

    
dfNew.to_csv("testALLColumns.csv")
print(dfNew)

# from datetime import datetime
