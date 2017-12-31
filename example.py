import sys
import datetime
import logging

from local_concert_playlist import (
    filter_events,
    OhMyRocknessAPI,
    SpotifyPlaylist
)

if __name__ == '__main__':
    playlist_name = 'OhMyRockness January 2018 Concerts'
    start_date = datetime.date(2018, 1, 1)
    end_date = start_date + datetime.timedelta(days=30)

    ohmyrockness = OhMyRocknessAPI()
    print('Querying OhMyRockness for Events')
    events = ohmyrockness.parsed_events(
       start_date=start_date,
       end_date=end_date,
       limit=1000
    )
    print('Obtained {} events'.format(len(events)))
    events = filter_events(
        events,
        include_city='New York'
    )
    print('Filtered to {} events'.format(len(events)))

    print('Connecting to Spotify')
    p = SpotifyPlaylist()

    print('Obtaining tracks corresponding to events on Spotify')
    selected_tracks = p.select_tracks_for_events(
        events,
        max_tracks=50,
        max_tracks_per_performer=3,
        offset_popularity=3.0
    )
    print('Obtained {} tracks from {} performers'.format(
        len(selected_tracks),
        len(set([track['artist_id'] for track in selected_tracks]))
    ))

    print('Creating Spotify playlist from selected tracks')
    p.create_playlist(
        playlist_name,
        selected_tracks,
        public=False
    )
    print('Spotify playlist has been created')
