
import snowflake.connector
import urllib.parse
import os
import signal
import json
import requests

# This mimics our setup of the token fetcher in the SnowCLI in the future.
ctx = snowflake.connector.connect(
    user="madkins",
    password="July2892!", # insert password here
    account="AWB48767",
    port=443,
    protocol="https",
    session_parameters={
        'PYTHON_CONNECTOR_QUERY_RESULT_FORMAT': 'json'
    })

# obtain the token, this token is valid for 6 hours and can be reused.
token_data = ctx._rest._token_request('ISSUE')
print("Snowflake Token: {}".format(token_data['data']['sessionToken']))
token_extract = token_data['data']['sessionToken']

# craft the request to ingress endpoint with authz
#token = f'\"{token_extract}\"'
#headers = {'Authorization': f'Snowflake Token={token}'}
#url = f'https://kgke-temptest-xaccounttest2.dev-snowflakecomputing.app/'

# validate the connection 
#response = requests.post(f'{url}', headers=headers)
#print(response.text)

# insert your code to interact with the application here ..