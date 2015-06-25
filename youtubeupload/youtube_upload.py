import json
import time

import requests

# Enter your credentials from https://console.developers.google.com/project/kurbelkamera/apiui/credential
CLIENT_ID     = '##########'
CLIENT_SECRET = '##########'
ACCESS_TOKEN  = ''
REFRESH_TOKEN = ''
TOKEN_TYPE    = ''


# send POST Request to youtube to get Device Code
r = requests.post(
    url='https://accounts.google.com/o/oauth2/device/code',
    data={
        'client_id': CLIENT_ID,
        'scope': 'https://www.googleapis.com/auth/youtube.upload'
    })

device_code_response = json.loads(r.text)
# print(json.dumps(device_code_response, indent=2))
print('URL:  {}\nCODE: {}'.format(device_code_response['verification_url'],device_code_response['user_code']))


# Poll every 5 seconds until user entered Code on the strange google-auth website
while True:
    r = requests.post(
        url='https://accounts.google.com/o/oauth2/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': device_code_response['device_code'],
            'grant_type': 'http://oauth.net/grant_type/device/1.0'
        }
    )

    response = json.loads(r.text)


    if 'error' in response:
        print('.')
        time.sleep(device_code_response['interval'])
    else:
        response = json.loads(r.text)
        ACCESS_TOKEN = response['access_token']
        REFRESH_TOKEN = response['refresh_token']
        TOKEN_TYPE = response['token_type']

        break

print('ACCESS_TOKEN',  ACCESS_TOKEN)
print('REFRESH_TOKEN', REFRESH_TOKEN)


# this stuff is not yet working
files = {'file': open('test.mp4', 'rb')}
parameters = {'part':''}

r = requests.post(
    url     = 'https://www.googleapis.com/upload/youtube/v3/videos',
    headers = {'Authorization': TOKEN_TYPE + ' ' + ACCESS_TOKEN},
    files=files
)



