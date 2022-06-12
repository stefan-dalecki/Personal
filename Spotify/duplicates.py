"""Detect duplicate playlists information"""
from __future__ import annotations
from collections import defaultdict
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = sp.user_playlists(user="sdalecki")

all_months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
alle_monaten = [
    "Januar",
    "Febuar",
    "Marz",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
]


class Songs:
    """Song data"""

    def __init__(self):
        self.songs = []
        self.playlists = None

    def __call__(self):
        """Detect any and all duplicates"""
        Songs.playlistgen(self)
        print("CALL BEGUN", end="\n" * 2)
        print(f"-out of {len(self.songs)} Total Songs")
        Songs.intraalbum_duplicates(self)
        Songs.interalbum_duplicates(self)
        print("\nCALL ENDED", end="\n" * 2)

    def playlistgen(self):
        """Identify playlists"""
        self.playlists = Songs.playlistsplit(self.songs, 0)

    def songs_for_emily(self, playlist: dict, months: list):
        """All songs from Emily's playlists

        Args:
            playlist (dict): a single playlist
            months (list): the playlist names (months)
        """
        if playlist["name"] in months:
            tracks = sp.playlist_tracks(playlist["uri"])
            for item in tracks["items"]:
                try:
                    artist = item["track"]["artists"][0]["name"]
                    song = item["track"]["name"]
                    song_id = (playlist["name"], song, artist)
                except TypeError:
                    pass
                self.songs += [song_id]

    @staticmethod
    def playlistsplit(exlist: list, ele: str) -> list:
        """Split playlist into components

        Args:
            exlist (list): list playlist info
            ele (str): element of interest

        Returns:
            list: all playlist data in altered list form
        """
        elelist = [i[ele] for i in exlist]
        cur = elelist[0]
        ind = [1, len(exlist)]
        for i, val in enumerate(elelist):
            if val != cur:
                ind.append(i)
                cur = val
        all_playlists = []
        ind.sort()
        for a, b in zip(ind, ind[1:]):
            all_playlists.append(exlist[a:b])
        return all_playlists

    def interalbum_duplicates(self):
        """Check for duplicate songs between albums"""
        artsong = [i[1:] for i in self.songs]
        months = [i[0] for i in self.songs]
        tally = defaultdict(list)
        for i, item in enumerate(artsong):
            tally[item].append(i)
        dupartsong = sorted([key, locs] for key, locs in tally.items() if len(locs) > 1)
        for dup in dupartsong:
            dupmonths = [months[i] for i in dup[1]]
            dup[1] = dupmonths
        if dupartsong:
            print("\n---inter-album duplicates found")
            for i in dupartsong:
                print(i)
        else:
            print("\n---no inter-album duplicates found")

    def intraalbum_duplicates(self):
        """Check for duplicate artists within an album"""
        intradups = []
        for i, playlist in enumerate(self.playlists):
            artists = [(i[2]) for i in playlist]
            songs = [i[1] for i in playlist]
            month = playlist[3][0]
            tally = defaultdict(list)
            for i, item in enumerate(artists):
                tally[item].append(i)
            dupartist = sorted(
                [key, locs] for key, locs in tally.items() if len(locs) > 1
            )
            if dupartist:
                for i in dupartist[0][1]:
                    i = songs[i]
                    dupartist.append(i)
                del dupartist[0][1]
                dupartist[0] = dupartist[0][0]
                dupartist.insert(0, month)
                intradups.append(dupartist)
        if intradups:
            print("\n---intra-album duplicate(s) found")
            for dup in intradups:
                print(f"\n-{dup[0]}\n--{dup[1]}")
                for song in dup[2:]:
                    print(f"---{song}")

        else:
            print("\n---no intra-album duplicates found")


music = Songs()
print("\n---Identifying Playlists---\n")
while playlists:
    for index, emilys_playlist in enumerate(playlists["items"]):
        music.songs_for_emily(emilys_playlist, all_months + alle_monaten)
    if playlists["next"]:
        playlists = sp.next(playlists)
    else:
        playlists = None
print("---Playlists Identified---", end="\n" * 3)
music()
