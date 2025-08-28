import configparser

import upstox_client
from upstox_client.rest import ApiException


alreadyLoggedIn = False

import requests
# client_id=''
client_id = '' 
url = 'https://api.upstox.com/v2/user/profile'
headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer {your_access_token}'
}
response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())


# Create a configparser object
config = configparser.ConfigParser()

# Read the properties file
config.read('my.properties')

# Get a value from the properties file
##code = config['DEFAULT']['code']
if config.has_option('DEFAULT', 'token'):
    # Configure OAuth2 access token for authorization: OAUTH2
    configuration = upstox_client.Configuration()
    token = config['DEFAULT']['token']
    configuration.access_token = token

    alreadyLoggedIn = False
    print(
        "RETRY check out this [https://api-v2.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=


