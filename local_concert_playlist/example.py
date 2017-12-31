import sys
import datetime
import logging

from local_concert_playlist import playlist


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()


if __name__ == '__main__':
    playlist_name = 'Q1 2018 Friday/Saturday New York City Concerts'
    start_date = datetime.date(2018, 1, 1)
    end_date = start_date + datetime.timedelta(days=90)

    logger.info('Creating connections to SeatGeek and Spotify')
    p = Playlist()

    logger.info('Obtaining upcoming events from SeatGeek')
    events = p.seatgeek.events(
        start_date=start_date,
        end_date=end_date,
        event_type='concert',
        venue_city='New York',
        day_of_week={4, 5},  # We like to go to concerts on Friday and Saturday
        exclude_genre={'Jazz'}  # My wife doesn't like to go to jazz concerts
    )
    logger.info('Returned {} events'.format(len(events)))

    logger.info('Obtaining tracks corresponding to upcoming events on Spotify')
    selected_tracks = p.select_tracks_for_events(
        events,
        max_tracks=50,
        max_tracks_per_performer=3,
        offset_popularity=3.0
    )

    logger.info('Creating Spotify playlist from selected tracks')
    p.create_playlist(
        playlist_name,
        selected_tracks,
        public=False
    )
    logger.info('Spotify playlist has been created')
