import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
from collections import defaultdict

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = sp.user_playlists(user='sdalecki')
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
monaten = ['Januar', 'Febuar', 'Marz', 'April', 'Mai', 'Juni', 'Juli',
           'August', 'September', 'Oktober', 'November', 'Dezember']

class Songs:
    def __init__(self):
        self.songs = []
        self.playlists = []

    def __call__(self):
        print(f'{len(self.songs)} Total Songs')
        Songs.interalbum_duplicates(self)
        Songs.intraalbum_duplicates(self)

    def playlists(user):
        return sp.user_playlists(user=user)

    def songs_for_emily(self, playlist, months):
        if playlist['name'] in months:
            tracks = sp.playlist_tracks(playlist['uri'])
            for item in tracks['items']:
                try:
                    artist = item['track']['artists'][0]['name']
                    song = item['track']['name']
                    id = (playlist['name'], song, artist)
                except Exception:
                    continue
                self.songs += [id]

    def interalbum_duplicates(self):
        artsong = [i[1:] for i in self.songs]
        months = [i[0] for i in self.songs]
        dupinfo = []
        tally = defaultdict(list)
        for i,item in enumerate(artsong):
            tally[item].append(i)
        dupartsong = sorted([key, locs] for key, locs in tally.items() if len(locs)>1)
        for dup in dupartsong:
            dupmonths = [months[i] for i in dup[1]]
            dup[1] = dupmonths
        if dupartsong:
            for i in dupartsong:
                print(i)
        else:
            print('no inter-album duplicates found')

    def intraalbum_duplicates(self):
        pass

music = Songs()
while playlists:
    for i, playlist in enumerate(playlists['items']):
        tracks = music.songs_for_emily(playlist, months+monaten)
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
music()
