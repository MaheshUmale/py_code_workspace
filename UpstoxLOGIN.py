import configparser

import upstox_client
from upstox_client.rest import ApiException

import pandas as pd
import numpy as np
from binance.client import Client
import logging
import plotly.graph_objects as go

# Set logging configuration
logging.basicConfig(level=logging.INFO)
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 1000)

alreadyLoggedIn = False

# Create a configparser object
config = configparser.ConfigParser()

# Read the properties file
#config.read('my.properties')

# Get a value from the properties file
##code = config['DEFAULT']['code']
if config.has_option('DEFAULT', 'token'):
    # Configure OAuth2 access token for authorization: OAUTH2
    configuration = upstox_client.Configuration()
    token = config['DEFAULT']['token']
    configuration.access_token = token
    #alreadyLoggedIn = True


def login_to_upstox(code):
    global alreadyLoggedIn
    if alreadyLoggedIn == False:
        # create an instance of the API class
        api_instance = upstox_client.LoginApi()
        api_version = '2.0'  # str | API Version Header
        # code = '' # str |  (optional)
        client_id = ''  # str |  (optional)
        client_secret = ''  # str |  (optional)
        redirect_uri = 'http://127.0.0.1:5000/upstox/callback' # 'http://127.0.0.1:5000'  #'http://127.0.0.1:5000/upstox/callback' #  'http://127.0.0.1:5000'  # str |  (optional)
        grant_type = 'authorization_code'  # str |  (optional)

        # Configure OAuth2 access token for authorization: OAUTH2
        configuration = upstox_client.Configuration()

        try:
            # Get token API
            api_response = api_instance.token(api_version, code=code, client_id=client_id, client_secret=client_secret,
                                              redirect_uri=redirect_uri, grant_type=grant_type)
            print(api_response)
            configuration.access_token = api_response.access_token
            # Write a value to the properties file
            # Create a configparser object
            config = configparser.ConfigParser()

            print(api_response.access_token)
            # Read the properties file
            config.read('my.properties')
            config['DEFAULT']['code'] = code
            config['DEFAULT']['token'] = configuration.access_token
            print(code)
            print(configuration.access_token)
            alreadyLoggedIn = True

            # Save the properties file
            with open('my.properties', 'w') as f:
                config.write(f)
                print(config)

            return configuration.access_token
        except ApiException as e:
            alreadyLoggedIn = False
            print("Exception when calling LoginApi->token: %s\n" % e)
            print(
                "RETRY check out this [https://api-v2.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=

login_to_upstox("CAFbwf")
