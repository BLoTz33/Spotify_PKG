from numpy import transpose
import numpy as np
import pandas as pd
import base64
import requests
from sklearn.preprocessing import MinMaxScaler

def Retrive_ids(dataset, col):
    url_array = dataset.iloc[:,col].values
    i = 0
    while i < len(url_array):
        start_string = 'spotify:track:'
        url_array[i] = url_array[i].replace(start_string,'')
        i += 1
    return url_array

def split_Charts(url_data):
    i = 0
    j = 100
    new1 = []
    new2 = []
    while i < 100:
        new1.append(url_data[i])
        i += 1
    while j < 200:
        new2.append(url_data[j])
        j += 1
    new1 = transpose(new1)
    new2 = transpose(new2)

    return new1, new2

def Radar_Plot(df):
    names = df.columns
    scaler = MinMaxScaler()
    Norm_Data = scaler.fit_transform(df)
    scaled_dt = pd.DataFrame(Norm_Data, columns=names)
    means = scaled_dt.mean(axis=0).values
    radar = np.append(means, means[0])
    radar_placement = np.linspace(0, 2 * np.pi, len(radar))
    label_placement = np.linspace(0,2*np.pi,len(means))
    return radar, radar_placement,label_placement

def Dataframe_Audio_features(list):
    new = pd.DataFrame(list)
    return new


class SpotifyAPI:

    def __init__(self,Client_ID, Client_Secret):
        self.Client_ID = Client_ID
        self.Client_Secret = Client_Secret

    def Get_Token(self):
        auth_url = 'https://accounts.spotify.com/api/token'
        Grant_token = {'grant_type': 'client_credentials'}
        client_creds = f'{self.Client_ID}:{self.Client_Secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode())
        token_header = {
            'Authorization': f'Basic {client_creds_b64.decode()}'
        }
        auth_response = requests.post(auth_url, data=Grant_token, headers=token_header)
        if auth_response.status_code in range(200, 299):
            token_respone = auth_response.json()
            self.access_token = token_respone['access_token']
            print('Token Aquired')
            return self.access_token
        else:
            print('Failed to get Token')
            self.access_token = None
            return self.access_token

    def Get_track_ids(self, Dict, Dict_ids):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
        }
        for key in Dict:
            if self.access_token is None or False:
                print('Must Have Access Token')
                return None
            playlist_id = Dict[key]
            request_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
            pr = requests.get(request_url, headers=headers)
            if pr.status_code:
                playlist_data = pr.json().get('items')
                for tr in playlist_data:
                    track_id = tr.get('track').get('id')
                    Dict_ids[key].add(track_id)



    def Get_audio_features(self,playlists,list):
        track_retrive_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
        }
        if self.access_token is False or None:
            print('Must Have Access Token')
            return None
        self.playlist = playlists
        j = 0
        for key1 in playlists:
            id_list = playlists[key1]
            for i in id_list:
                request_url = f'https://api.spotify.com/v1/audio-features/{i}'
                pr = requests.get(request_url, headers=track_retrive_header)
                if pr.status_code in range(200, 299):
                    track_features = pr.json()
                    track_data_copy = track_features.copy()
                    list[j].append(track_data_copy)
                    print('yes', i)

                else:
                    print('Audio Features failed to aquire!')
                    break
            j += 1
            if pr.status_code not in range(200, 299):
                print('function did not complete')
                break


