import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
from collections import defaultdict
from itertools import chain

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
        print('~~~CALL BEGUN~~~', end='\n'*2)
        print(f'{len(self.songs)} Total Songs', end='\n'*2)
        Songs.intraalbum_duplicates(self)
        Songs.interalbum_duplicates(self)
        print('\n~~~CALL ENDED~~~', end='\n'*2)

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
            print('\ninter-album duplicates found')
            for i in dupartsong:
                print(i)
        else:
            print('\nno inter-album duplicates found')

    def intraalbum_duplicates(self):
        playsongs = [self.songs[i:i+15] for i in range(0, len(self.songs), 15)]
        intradups = []
        for i, playlist in enumerate(playsongs):
            artists = [(i[2]) for i in playlist]
            songs = [i[1] for i in playlist]
            month = playlist[3][0]
            tally = defaultdict(list)
            for i, item in enumerate(artists):
                tally[item].append(i)
            dupartist = sorted([key, locs] for key, locs in tally.items() if len(locs)>1)
            if dupartist:
                for i in dupartist[0][1]:
                    i=songs[i]
                    dupartist.append(i)
                del dupartist[0][1]
                dupartist[0]=dupartist[0][0]
                dupartist.insert(0, month)
                intradups.append(dupartist)
        if intradups:
            print('\nintra-album duplicate(s) found')
            for dup in intradups:
                print(f'\n-{dup[0]}\n--{dup[1]}')
                for song in dup[2:]:
                    print(f'---{song}')

        else:
            print('\nno intra-album duplicates found')

music = Songs()
while playlists:
    for i, playlist in enumerate(playlists['items']):
        tracks = music.songs_for_emily(playlist, months+monaten)
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
music()
