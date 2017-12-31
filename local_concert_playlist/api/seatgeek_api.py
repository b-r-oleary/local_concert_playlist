import datetime

from local_concert_playlist.api.base import APIInterface
from local_concert_playlist.model import (
    Genre,
    Event,
    Performer,
    Venue
)


class SeatGeekAPI(APIInterface):
    """
    This object provides an interface to the SeatGeek API:
    http://platform.seatgeek.com/
    API credentials can be obtained from:
    https://seatgeek.com/account/develop

    Currently, this object only supports queries for lists of
    upcoming events.

    Parameters
    ----------
    client_id (str): SeatGeek API client id
    client_secret (str): SeatGeek API client secret
    """
    base_url = "https://api.seatgeek.com/2"

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = self._get_credentials(
            client_id,
            'SEATGEEK_CLIENT_ID'
        )
        self.client_secret = self._get_credentials(
            client_secret,
            'SEATGEEK_CLIENT_SECRET'
        )

    def get(self, path, params, headers=None):
        params.update(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return super(SeatGeekAPI, self).get(path, params, headers=headers)

    def events(self,
               per_page=1000,
               page=1,
               geoip=True,
               sort='score.desc',
               start_date=None,
               end_date=None,
               event_type='concert',
               venue_city='New York',
               has_listings=True,
               min_price_below=None):
        """
        Obtain a list of events from the SeatGeek API.

        Parameters
        ----------
        per_page: (int) - maximum number of events to return on each API call,
            default 1000
        page: (int) - page index for this API call
        geoip: (bool) - Whether or not to use IP geolocation to filter to
            nearby events, default True
        sort: (str) - A string that describes a sorting method that is accepted
            by the SeatGeek API, default 'score.desc'
        start_date: (datetime.date) - lower bound for event dates, default None
        end_date: (datetime.date) - upper bound for event dates, default None
        event_type: (str) - A string that describes an event type that is
            accepted by the SeatGeek API, default 'concert'
        venue_city: (str) - filter events to only those that will take
            place in a specified set of venue cities
        has_listings: (bool) - filter to events that currently have listings
            on SeatGeek.
        min_price_below: (float) - filter to events that have ticket prices
            below a specified value.

        Returns
        -------
        A list of event objects from the SeatGeek API
        """

        params = {
            'per_page': per_page,
            'page': page
        }
        if geoip:
            params['geoip'] = 'true'
        if sort is not None:
            params['sort'] = sort
        if has_listings:
            params['listing_count.gt'] = 0
        if min_price_below is not None:
            params['lowest_price.lte'] = int(min_price_below)
        if start_date is not None:
            params['datetime_utc.gte'] = self._parse_date(start_date)
        if end_date is not None:
            params['datetime_utc.lte'] = self._parse_date(end_date)
        if venue_city is not None:
            params['venue.city'] = venue_city
        if event_type is not None:
            params['taxonomies.name'] = event_type

        return self.get('events', params).get('events', [])

    def _parse_event(self, event):
        """
        Parse a raw json event response object into an `Event` object
        """
        source = self.__class__.__name__
        event_name = event['title']
        datetime_local = datetime.datetime.strptime(
            event['datetime_local'],
            '%Y-%m-%dT%H:%M:%S'
        )
        performers = [
            Performer(
                source,
                performer['id'],
                performer['name'],
                [
                    Genre(source, genre['id'], genre['name'])
                    for genre in performer.get('genres', [])
                ]
            )
            for performer in event['performers']
        ]
        venue = Venue(
            source,
            event['venue']['id'],
            event['venue']['name'],
            '\n'.join([
                event['venue']['address'],
                event['venue']['extended_address']
            ]),
            event['venue']['city']
        )
        return Event(
            source,
            event['id'],
            event['title'],
            datetime_local,
            venue,
            performers
        )
