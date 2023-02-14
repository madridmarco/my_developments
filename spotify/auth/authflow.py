import requests
import base64
from os import path
import webbrowser
import urllib.parse
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from datetime import timedelta
import json

code_auth = None
class RequestHandler(BaseHTTPRequestHandler):
    '''
        BaseHTTPRequestHandler from the http.server module. This class is used to handle the redirect 
        URL sent by Spotify when the authorization code is obtained. The do_GET method captures the 
        authorization code from the query string in the URL and stores it in the code_auth global variable.
    '''
    def do_GET(self):
        global code_auth
        self.close_connection = True
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code_auth = query['code']

class AuthFlow: 
    '''
        The script defines the AuthFlow class, which takes the client ID and client secret of your 
        Spotify app as input when instantiated. The class has methods to obtain an authorization code, 
        refresh an access token, and get the access token.
    '''

    __data = path.join('auth','param','parameters.json')
    __endpoin_auth = 'https://accounts.spotify.com/authorize'
    __endpoin_token = 'https://accounts.spotify.com/api/token'
    __redirect_uri = 'http://localhost:8080'

    def __init__(self,client_id,client_secret):

        '''
            The __init__ In the __init__ method, the client ID and client secret are encoded into a base64-encoded string 
            and saved in the __credentials_auth variable. The authorization code is requested by 
            making a POST request to the __endpoint_token URL, passing the required parameters in the request 
            body. If the response is successful,the access token and the expiry date are saved in a JSON file.'
        '''

        self.client_id = client_id
        self.client_secret =  client_secret
        self.__credencials_auth = base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()

        self.__data_token =  {'grant_type' : 'authorization_code',
            'code' : self.__get_code_auth(),
            'redirect_uri' : AuthFlow.__redirect_uri
        }

        self.__headers_auth = {'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.__credencials_auth}"
        }
    
        self.__response =requests.post(url = self.__endpoin_token, data= self.__data_token, headers= self.__headers_auth)

        if self.__response:
            data_json = self.__response.json()
            self.__save_data_json(data_json)
            self.__token = data_json['access_token']
        else:
            print('Error Respuesta!!!') 

    def token(self):
        '''
            The token method returns the access token. If the access token has not expired, it returns the saved token. 
            If the token has expired, it makes a POST request to the __endpoint_token URL to refresh the access token 
            using the refresh token. If the response is successful, the new access token is returned, 
            otherwise an error message is displayed.
        '''
        data = self.__open_json()
        if datetime.now() < datetime.strptime(data['date_expirian'] , '%Y-%m-%d %H:%M:%S.%f'):
            return self.__token
        else:
            param_refres_token = {'grant_type' : 'refresh_token',
                'refresh_token' : data['refresh_token']
            }
            headers_auth = {'Accept': 'application/json',
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {self.__credencials_auth}"
            }
            response = requests.post(AuthFlow.__endpoin_token, data= param_refres_token, headers= headers_auth)

            if response:
                data_json = response.json()
                return data_json['access_token']
            else:
                print('Error Respuesta')

    def __get_code_auth(self):
        '''
            This method is used to obtain the authorization code by making a GET request to the __endpoint_auth URL and passing the required parameters 
            in the request. The authorization code is obtained by opening the URL in a web browser and capturing the code from the redirect URL.
            The code also defines the Request
        '''
        params_auth = {'response_type' : 'code',
             'client_id' :self.client_id,
             'scope' : 'user-top-read',
             'redirect_uri' : AuthFlow.__redirect_uri
        } 

        response = requests.get(url = AuthFlow.__endpoin_auth, params= params_auth)
        
        if response:
            webbrowser.open_new_tab(response.url)
            server = HTTPServer(('localhost', 8080), RequestHandler)
            server.handle_request()
            return code_auth
        else:
            print('Error Respuesta!!!', response)

    def __open_json(self):
        '''
            The private method __open_json is created to load the data stored in a JSON file which is used to retrieve the 
            data when the token method is called to return the access token. If the access token has expired, the method can 
            be used to upload the refresh token so that a new access token can be obtained.
        '''
        with open(AuthFlow.__data) as f:
            data = json.load(f)
        return data

    def __save_data_json(self,data):

        dic_token = {'date_expirian' : f'{datetime.now() + timedelta(seconds= data["expires_in"])}',
            'access_token' : data['access_token'],
            'refresh_token' : data["refresh_token"]
        }
        
        with open(AuthFlow.__data, 'w') as f:
            json.dump(dic_token ,f)