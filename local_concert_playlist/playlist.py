import os
import time

import numpy as np

from seatgeek_api import (
    SeatGeekAPI,
    group_events_by_performers
)
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util


class Playlist(object):
    credentials = {
        env_var: os.getenv(env_var)
        for env_var in [
            'SPOTIFY_USERNAME',
            'SPOTIFY_USER_SCOPE',
            'SPOTIFY_REDIRECT_URI',
            'SPOTIFY_CLIENT_ID',
            'SPOTIFY_CLIENT_SECRET',
            'SEATGEEK_CLIENT_ID',
            'SEATGEEK_CLIENT_SECRET'
        ]
    }
    spotify_request_timeout = .03

    def __init__(self):
        self.spotify = self._get_spotify_connection()
        self.seatgeek = self._get_seatgeek_connection()

    def _get_spotify_connection(self):
        user_token = spotipy.util.prompt_for_user_token(
            self.credentials['SPOTIFY_USERNAME'],
            scope=self.credentials['SPOTIFY_USER_SCOPE'],
            client_id=self.credentials['SPOTIFY_CLIENT_ID'],
            client_secret=self.credentials['SPOTIFY_CLIENT_SECRET'],
            redirect_uri=self.credentials['SPOTIFY_REDIRECT_URI']
        )

        spotify = Spotify(
            auth=user_token,
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self.credentials['SPOTIFY_CLIENT_ID'],
                client_secret=self.credentials['SPOTIFY_CLIENT_SECRET']
            )
        )
        return spotify

    def _get_seatgeek_connection(self):
        seatgeek = SeatGeekAPI(
            self.credentials['SEATGEEK_CLIENT_ID'],
            self.credentials['SEATGEEK_CLIENT_SECRET']
        )
        return seatgeek

    def _filter_tracks(self,
                       tracks,
                       limit=100,
                       likelihood=None,
                       offset_popularity=3.0):

        if len(tracks) <= limit:
            selected_tracks = tracks
        else:
            if likelihood is None:
                def popularity_likelihood(track):
                    popularity = float(track['sp_track_popularity'])
                    if popularity < offset_popularity:
                        return offset_popularity
                    else:
                        return popularity

                likelihood = popularity_likelihood

            prob = np.abs(np.array(map(likelihood, tracks)))
            prob = prob / np.sum(prob)

            selected_tracks = np.random.choice(
                tracks,
                size=limit,
                replace=False,
                p=prob
            )

        return sorted(
            selected_tracks,
            key=lambda track: track['sp_track_popularity']
        )

    def _get_tracks_for_events(self,
                               events,
                               max_tracks_per_performer=2):

        performers = group_events_by_performers(events)
        tracks = []

        for pid, performer in performers.iteritems():
            artist_search_results = self.spotify.search(
                performer['name'],
                type='artist'
            )
            artists = artist_search_results['artists']['items']
            if len(artists) == 0:
                # failure to find an artist on spotify
                continue

            artist_id = artists[0]['id']
            top_tracks_results = self.spotify.artist_top_tracks(artist_id)
            top_tracks = top_tracks_results['tracks']

            for i, top_track in enumerate(top_tracks):
                if i >= max_tracks_per_performer:
                    break

                tracks.append({
                    'sg_performer_id': pid,
                    'sg_performer_name': performer['name'],
                    'sg_performer_popularity': performer['popularity'],
                    'sp_artist_id': artist_id,
                    'sp_track_id': top_track['id'],
                    'sp_track_uri': top_track['uri'],
                    'sp_track_name': top_track['name'],
                    'sp_track_popularity': top_track['popularity']
                })

            time.sleep(self.spotify_request_timeout)
        return tracks

    def select_tracks_for_events(self,
                                 events,
                                 max_tracks=30,
                                 max_tracks_per_performer=3,
                                 track_likelihood=None,
                                 offset_popularity=3.0):

        tracks = self._get_tracks_for_events(
            events,
            max_tracks_per_performer=max_tracks_per_performer
        )
        selected_tracks = self._filter_tracks(
            tracks,
            limit=max_tracks,
            likelihood=track_likelihood,
            offset_popularity=offset_popularity
        )
        return selected_tracks

    def create_playlist(self, playlist_name, tracks, public=False):
        spotify_username = self.credentials['SPOTIFY_USERNAME']
        playlist = self.spotify.user_playlist_create(
            spotify_username,
            playlist_name,
            public=public
        )
        updated_playlist = self.spotify.user_playlist_add_tracks(
            spotify_username,
            playlist['id'],
            [track['sp_track_uri']
             for track in tracks]
        )
        return updated_playlist
