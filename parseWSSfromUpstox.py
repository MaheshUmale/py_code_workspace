import pandas as pd
import json
from io import StringIO

# Parsing JSON data using pandas
import os
import fnmatch

def list_files_by_pattern(directory, pattern):
    """Returns a list of files in a directory matching a given pattern."""
    return fnmatch.filter(os.listdir(directory), pattern)

# Example: List all .txt files in the current directory
# files = list_files_by_pattern('.', '*.txt')

fileList = list_files_by_pattern('.', 'xxxupstox_WSS_output_*.txt')
print(fileList)
def appendCSVToFile():
    
    wssData = pd.DataFrame()    
    for file in fileList :
        df = pd.read_json(file, lines=True)
        print(f'started file {file}')
        for row in df['feeds'] :
            #print(row)
            #print(pd.json_normalize(row))
            data = pd.json_normalize(row)
            ltt = 00
            ltp =0.0
            ltq = 00
            symbol = ''
            for key, value in data.items():
                val = str(key).split('.')
                symbol = val[0]
                for inner_key, inner_value in value.items():
                    #print(f"KEY  {key}: VALUE {inner_value}")
                    if(val[2] == 'ltp') :
                        ltp = inner_value
                    elif (val[2] == 'ltt') :
                        ltt = inner_value
                    elif(val[2] == 'ltq') :
                        ltq = inner_value
                    elif (val[2] == 'cp'):

                        string_data = "\'"+symbol+"\',"+str(ltt)+","+str(ltp)+","+str(ltq)
                        df_from_string = pd.read_csv(StringIO(string_data), header=None)
                        df_from_string.columns = ['symbol','ltt','ltp','ltq']
                        wssData = wssData._append(df_from_string, ignore_index=True)
                        ltt = 00
                        ltp = 0.0
                        ltq = 00
                        symbol = ''
        print(f'completed file {file}')

    #print(wssData)
    df_sorted = wssData.sort_values(by='ltt')
    df_sorted.to_csv('upstox_WSS_output_combined.csv', index = False)
    print( " CONVERTED TO CSV to load as DF ")


appendCSVToFile()