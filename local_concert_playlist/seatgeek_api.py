import copy
import datetime
import os
import urllib

import requests


class SeatGeekAPI(object):
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

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get(self, path, **params):
        params.update(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        url = "{}?{}".format(
            os.path.join(self.base_url, path),
            urllib.urlencode(params)
        )
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def _parse_date(self, date):
        date_format = "%Y-%m-%d"
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, date_format)
        elif isinstance(date, (datetime.date, datetime.datetime)):
            pass
        else:
            raise ValueError(
                'expect datetime.date objects or string dates with format {}'
                .format(date_format)
            )
        return date.strftime(date_format)

    def _events(self,
                geoip=True,
                sort='score.desc',
                start_date=None,
                end_date=None,
                event_type='concert',
                venue_city='New York',
                has_listings=True,
                min_price_below=None,
                per_page=2500,
                page=1):

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

        return self.get('events', **params)

    def _filter_events(self,
                       events,
                       day_of_week=None,
                       venue=None,
                       exclude_venue=None,
                       genre=None,
                       exclude_genre=None):

        def filter_func(event):
            datetime_format = '%Y-%m-%dT%H:%M:%S'
            local_time = datetime.datetime.strptime(
                event['datetime_local'],
                datetime_format
            )
            output = True
            if day_of_week is not None:
                output &= local_time.weekday() in day_of_week
            if venue is not None:
                output &= event['venue']['name'] in venue
            if exclude_venue is not None:
                output &= event['venue']['name'] not in exclude_venue
            if genre is not None:
                output &= any(
                    g['name'] in genre
                    for performer in event['performers']
                    for g in performer.get('genres', [])
                )
            if exclude_genre is not None:
                output &= any(
                    g['name'] not in exclude_genre
                    for performer in event['performers']
                    for g in performer.get('genres', [])
                )
            return output

        return {
            'meta': events['meta'],
            'events': filter(
                filter_func,
                events['events']
            )
        }

    def events(self,
               geoip=True,
               sort='score.desc',
               start_date=None,
               end_date=None,
               event_type='concert',
               limit=5000,
               per_page=1000,
               venue_city=None,
               day_of_week=None,
               venue=None,
               exclude_venue=None,
               genre=None,
               exclude_genre=None,
               has_listings=None,
               min_price_below=None):
        """
        Obtain a list of events from the SeatGeek API.

        Parameters
        ----------
        geoip: (bool) - Whether or not to use IP geolocation to filter to
            nearby events, default True
        sort: (str) - A string that describes a sorting method that is accepted
            by the SeatGeek API, default 'score.desc'
        start_date: (datetime.date) - lower bound for event dates, default None
        end_date: (datetime.date) - upper bound for event dates, default None
        event_type: (str) - A string that describes an event type that is
            accepted by the SeatGeek API, default 'concert'
        limit: (int) - maximum number of events to return, default 1000
        per_page: (int) - maximum number of events to return on each API call,
            default 1000
        venue_city: (set of str) - filter events to only those that will take
            place in a specified set of venue cities
        day_of_week: (set of int) - filter events to only those that will take
            place on certain days of the week (0=Monday, ...,  6=Sunday)
        venue: (set of str) - filter events to only those that will take place
            in certain venues
        exclude_venue: (set of str) - filter out events at certain venues
        genre: (set of str) - filter events to only those with performers that
            are characterized by certain genres
        exclude_genre: (set of str) - filter out events with performers that
            are characterized by certain genres
        has_listings: (bool) - filter to events that currently have listings
            on SeatGeek.
        min_price_below: (float) - filter to events that have ticket prices
            below a specified value.
        """

        events = {
            'meta': None,
            'events': []
        }
        page = 1
        while True:
            e = self._events(
                geoip=geoip,
                sort=sort,
                start_date=start_date,
                end_date=end_date,
                event_type=event_type,
                venue_city=venue_city,
                has_listings=has_listings,
                min_price_below=min_price_below,
                per_page=per_page,
                page=page
            )

            fe = self._filter_events(
                e,
                day_of_week=day_of_week,
                venue=venue,
                exclude_venue=exclude_venue,
                genre=genre,
                exclude_genre=exclude_genre
            )

            events['meta'] = fe['meta']
            events['events'].extend(fe['events'])

            if len(events['events']) >= limit:
                events['events'] = events['events'][:limit]
                break

            if len(e['events']) >= per_page:
                page += 1
                continue
            else:
                break

        return events


def group_events_by_performers(events):
    """
    Given an events reponse from the SeatGeek API, group
    events by performers that are performing in those events.

    Parameters
    ----------
    events (list) - response from SeatGeekAPI.events

    Returns
    -------
    output (dict) - mapping from a SeatGeek performer_id to
        a dict with performer attributes and a list of corresponding
        events
    """
    output = {}
    for event in events['events']:

        event_copy = copy.deepcopy(event)
        del event_copy['performers']

        for performer in event['performers']:
            if performer['id'] not in output:
                output[performer['id']] = copy.deepcopy(performer)
                output[performer['id']]['events'] = []

            output[performer['id']]['events'].append(event_copy)

    return output
