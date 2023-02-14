from auth.authflow import AuthFlow
import requests
import sys

def main():
    '''
        This code  retrieves the user's top 10 long-term listened-to artists from the Spotify API using OAuth2.0 
        for authentication. The response is in JSON format, 
        and the code prints out the names of the artists in a list.
    
    '''

    client_id_ = '<your client_id>'
    client_secret = '<your client_secret>'
    auth = AuthFlow(client_id= client_id_, client_secret= client_secret)
    token = auth.token()
    param = { 'Authorization' : f'Bearer {token}','Accept': 'application/json'}

    response = requests.get(f'https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=10' , headers= param)
    if response:
        data = response.json()
    else:
        print('Error Response!!')
    
    list_top_10_artists = [data['items'][i]['name'] for i in  range(len(data['items']))]
    return print(list_top_10_artists)

if __name__ == '__main__':
    sys.exit(main())